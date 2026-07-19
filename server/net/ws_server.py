"""Single-process WebSocket server entrypoint.

Pairs connections two at a time through AnonymousLobby (see its own
docstring for why this is deliberately trivial, throwaway scaffolding) - no
matchmaking/rooms yet (those land in later stages, all reusing GameRoom
unchanged). Login/register are handled per-connection (net/auth.py) but
don't yet gate room entry - AnonymousLobby pairs anonymous or authenticated
connections identically until real ELO matchmaking replaces it.
"""

import asyncio
from pathlib import Path

import websockets

from bus.event_bus import EventBus
from chess_io.board_parser import BoardParser
from config import DB_PATH, GAME_LOG_DIR, WS_HOST, WS_PORT
from model.starting_position import STARTING_POSITION
from net import auth, protocol
from net.anonymous_lobby import AnonymousLobby
from net.game_room import GameRoom
from net.session import Session
from persistence.db import connect as connect_db
from persistence.elo_updater import EloUpdater
from persistence.event_log import EventLogWriter
from persistence.users_repository import UsersRepository

_ROOM_HANDLERS = {
    protocol.REQUEST_MOVE: GameRoom.handle_request_move,
    protocol.REQUEST_JUMP: GameRoom.handle_request_jump,
}
_AUTH_HANDLERS = {
    protocol.LOGIN: auth.handle_login,
    protocol.REGISTER: auth.handle_register,
}


def _new_starting_board():
    return BoardParser().parse(STARTING_POSITION)


async def _dispatch(room: GameRoom, session: Session, users: UsersRepository, websocket, text: str) -> None:
    try:
        message = protocol.decode(text)
    except ValueError as exc:
        await websocket.send(protocol.encode(protocol.error("bad_message", str(exc))))
        return

    message_type = message["type"]
    auth_handler = _AUTH_HANDLERS.get(message_type)
    if auth_handler is not None:
        await websocket.send(protocol.encode(auth_handler(message, session, users)))
        return

    room_handler = _ROOM_HANDLERS.get(message_type)
    if room_handler is None:
        await websocket.send(protocol.encode(protocol.error("bad_message", f"unknown type: {message_type}")))
        return
    room_handler(room, message)


def make_handler(lobby: AnonymousLobby, users: UsersRepository):
    """Build the per-connection coroutine websockets.serve calls for each client."""

    async def handler(websocket) -> None:
        session = Session()
        room = await lobby.join(websocket)
        color = room.color_of(websocket)
        await websocket.send(protocol.encode(protocol.game_start(room.game_id, color, room.state_version, room.snapshot())))
        try:
            async for text in websocket:
                await _dispatch(room, session, users, websocket, text)
        finally:
            room.leave(websocket)

    return handler


async def serve(
    host: str = WS_HOST, port: int = WS_PORT, log_dir: Path = GAME_LOG_DIR, db_path: Path = DB_PATH,
):
    """Start listening on host:port, pairing connections two at a time.

    Returns the running Server (already accepting connections) - callers
    manage its lifetime themselves (`server.close()` + `await
    server.wait_closed()`). Returning it rather than blocking here is what
    lets tests bind an ephemeral port (port=0) and read back which one the
    OS actually picked via `server.sockets`. `log_dir`/`db_path` default to
    the real GAME_LOG_DIR/DB_PATH but are overridable so tests can point
    them at a temp dir instead of writing into the repo.
    """
    bus = EventBus()
    users = UsersRepository(connect_db(db_path))
    bus.subscribe_all(EventLogWriter(log_dir))
    bus.subscribe_all(EloUpdater(users))
    lobby = AnonymousLobby(bus, _new_starting_board)
    return await websockets.serve(make_handler(lobby, users), host, port)


async def _serve_forever(host: str = WS_HOST, port: int = WS_PORT) -> None:
    server = await serve(host, port)
    async with server:
        await asyncio.Future()  # run until cancelled/interrupted


if __name__ == "__main__":
    asyncio.run(_serve_forever())
