"""Single-process WebSocket server entrypoint.

Login gates matchmaking: a connection must send login/register before play
is accepted. Matchmaking (services/matchmaking_service.py) pairs
authenticated sessions within MATCH_ELO_RANGE, giving up with an error
after MATCHMAKING_WAIT_MS if no human match is found - superseding the
earlier anonymous-lobby pairing now that there's login/ELO to actually
match on.
"""

import asyncio
from pathlib import Path

import websockets

from bus.event_bus import EventBus
from config import (
    DB_PATH, DISCONNECT_GRACE_MS, GAME_LOG_DIR, MATCHMAKING_TICK_MS, MATCHMAKING_WAIT_MS, WS_HOST, WS_PORT,
)
import protocol
from gateway.connection import Connection
from persistence.db import connect as connect_db
from persistence.elo_updater import EloUpdater
from persistence.event_log import EventLogWriter
from persistence.users_repository import UsersRepository
from router import message_router
from services.game_registry import GameRegistry
from services.matchmaking_service import Matchmaking
from services.room_service import RoomRegistry


class Gateway:
    """Owns one connection's whole lifecycle: the read loop, decoding each
    inbound message, dispatching it through the router, and cleanup on
    disconnect. One instance per websocket, built fresh by make_handler()
    below.

    Kept as a class (not a bare closure) so run()/dispatch() stay directly
    unit-testable against fakes without a real socket - the same reasoning
    this class's pre-split predecessor (ConnectionHandler) already had.
    See server/tests/integration/test_ws_integration.py and
    test_full_flow.py for the real-socket end-to-end coverage this doesn't
    replace."""

    def __init__(self, websocket, router: dict, matchmaking: Matchmaking):
        self.connection = Connection(websocket)
        self._router = router
        # Needed directly (not just via the router): cleanup below calls
        # matchmaking.cancel() unconditionally on every disconnect,
        # bypassing message dispatch entirely, same as before the split.
        self._matchmaking = matchmaking

    async def dispatch(self, text: str | bytes) -> None:
        try:
            message = protocol.decode(text)
        except ValueError as exc:
            await self.connection.send(protocol.error("bad_message", str(exc)))
            return

        try:
            await message_router.dispatch(self._router, self.connection, message)
        except Exception as exc:
            # A well-formed-but-malformed message (e.g. request_move
            # missing "source") or any other bug in a single handler must
            # not take this connection down - let alone the room's other,
            # perfectly well-behaved player. asyncio.CancelledError is a
            # BaseException, not Exception, so real task cancellation
            # (server shutdown, etc.) still propagates.
            try:
                await self.connection.send(protocol.error("bad_message", f"could not process {message['type']}: {exc}"))
            except Exception:
                pass  # the connection itself may already be the thing that's gone

    async def run(self) -> None:
        try:
            async for text in self.connection.socket:
                await self.dispatch(text)
        finally:
            self._matchmaking.cancel(self.connection.socket)
            if self.connection.room is not None:
                self.connection.room.leave(self.connection.socket)
            if self.connection.viewing_room is not None:
                self.connection.viewing_room.leave_viewer(self.connection.socket)


def make_handler(matchmaking: Matchmaking, rooms: RoomRegistry, games: GameRegistry, users: UsersRepository):
    """Build the per-connection coroutine websockets.serve calls for each client."""
    router = message_router.build_router(matchmaking, rooms, games, users)

    async def handler(websocket) -> None:
        await Gateway(websocket, router, matchmaking).run()

    return handler


async def serve(
    host: str = WS_HOST, port: int = WS_PORT, log_dir: Path = GAME_LOG_DIR, db_path: Path = DB_PATH,
    matchmaking_tick_ms: int = MATCHMAKING_TICK_MS, matchmaking_wait_ms: int = MATCHMAKING_WAIT_MS,
    disconnect_grace_ms: int = DISCONNECT_GRACE_MS,
):
    """Start listening on host:port. Returns the running Server (already
    accepting connections) - callers manage its lifetime themselves
    (`server.close()` + `await server.wait_closed()`). Returning it rather
    than blocking here is what lets tests bind an ephemeral port (port=0)
    and read back which one the OS actually picked via `server.sockets`.
    `log_dir`/`db_path` default to the real GAME_LOG_DIR/DB_PATH, and the
    matchmaking/disconnect timings to their real config defaults, but all
    are overridable so tests can point at a temp dir and run matchmaking's
    timeout/forfeit timing fast instead of waiting on real wall-clock
    seconds (see server/tests/integration/test_full_flow.py).
    """
    bus = EventBus()
    users = UsersRepository(connect_db(db_path))
    bus.subscribe_all(EventLogWriter(log_dir))
    bus.subscribe_all(EloUpdater(users))

    games = GameRegistry(bus, disconnect_grace_ms=disconnect_grace_ms)
    matchmaking = Matchmaking(games.new_room, tick_ms=matchmaking_tick_ms, wait_ms=matchmaking_wait_ms)
    matchmaking.start()
    rooms = RoomRegistry(games.new_room)

    return await websockets.serve(make_handler(matchmaking, rooms, games, users), host, port)


async def _serve_forever(host: str = WS_HOST, port: int = WS_PORT) -> None:
    server = await serve(host, port)
    print(f"Server listening on {host}:{port}")
    async with server:
        await asyncio.Future()  # run until cancelled/interrupted


if __name__ == "__main__":
    asyncio.run(_serve_forever())
