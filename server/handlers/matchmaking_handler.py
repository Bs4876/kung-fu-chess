"""play / cancel_matchmaking."""

import protocol
from handlers.common import enter_room, require_authenticated


async def handle_play(connection, message: dict, matchmaking) -> None:
    if not await require_authenticated(connection):
        return
    await connection.send(protocol.matchmaking_status("searching"))
    game_room = await matchmaking.play(connection.socket, connection.session.user)
    if game_room is None:
        await connection.send(protocol.error("no_opponent_found", "no opponent found within the time limit"))
        return
    await enter_room(connection, game_room)


async def handle_cancel_matchmaking(connection, message: dict, matchmaking) -> None:
    matchmaking.cancel(connection.socket)
