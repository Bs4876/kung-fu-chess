"""Table-driven message dispatch: message_type -> handler. Generalizes the
old _ROOM_HANDLERS dict (which only ever covered request_move/request_jump)
to every message type, replacing gateway/ws_server.py's old if/elif chain -
one dispatch mechanism instead of two.
"""

from functools import partial

import protocol
from handlers import auth_handler, gameplay_handler, matchmaking_handler, rooms_handler


def build_router(matchmaking, rooms, games, users) -> dict:
    """Built once (see gateway/ws_server.py's make_handler) and shared by
    every connection - handlers that need a process-wide service get it
    closed over via functools.partial; gameplay_handler's two need none
    (the "service" they act on is per-connection state: connection.room)."""
    return {
        protocol.LOGIN: partial(auth_handler.handle_login, users=users),
        protocol.PLAY: partial(matchmaking_handler.handle_play, matchmaking=matchmaking),
        protocol.CANCEL_MATCHMAKING: partial(matchmaking_handler.handle_cancel_matchmaking, matchmaking=matchmaking),
        protocol.REJOIN_GAME: partial(rooms_handler.handle_rejoin_game, games=games),
        protocol.LIST_ROOMS: partial(rooms_handler.handle_list_rooms, rooms=rooms),
        protocol.CREATE_ROOM: partial(rooms_handler.handle_create_room, rooms=rooms),
        protocol.JOIN_ROOM: partial(rooms_handler.handle_join_room, rooms=rooms),
        protocol.CANCEL_ROOM: partial(rooms_handler.handle_cancel_room, rooms=rooms),
        protocol.WATCH_ROOM: partial(rooms_handler.handle_watch_room, rooms=rooms),
        protocol.REQUEST_MOVE: gameplay_handler.handle_request_move,
        protocol.REQUEST_JUMP: gameplay_handler.handle_request_jump,
    }


async def dispatch(router: dict, connection, message: dict) -> None:
    handler = router.get(message["type"])
    if handler is None:
        await connection.send(protocol.error("bad_message", f"unexpected message: {message['type']}"))
        return
    await handler(connection, message)
