"""Shared logic used by 2+ handler modules - doesn't belong to any single
domain handler on its own: matchmaking_handler and rooms_handler both need
require_authenticated/enter_room, and rooms_handler's join_room/watch_room
both need watch (seating as a read-only viewer).
"""

import protocol


async def require_authenticated(connection) -> bool:
    if connection.session.is_authenticated:
        return True
    await connection.send(protocol.error("not_authenticated", "log in first"))
    return False


async def enter_room(connection, game_room) -> None:
    connection.room = game_room
    color = game_room.color_of(connection.socket)
    # Every call site seats/re-seats connection.socket in game_room right
    # before calling this - color is only ever None for the (separate)
    # viewer path in watch(), never here.
    assert color is not None
    await connection.send(protocol.game_start(
        game_room.game_id, color, game_room.state_version, game_room.snapshot(),
        white_name=game_room.player_name("white"), black_name=game_room.player_name("black"),
    ))


async def watch(connection, game_room) -> None:
    game_room.add_viewer(connection.socket)
    connection.viewing_room = game_room
    # color=None marks this as a viewer's catch-up snapshot rather than
    # a seated player's game_start.
    await connection.send(protocol.game_start(
        game_room.game_id, None, game_room.state_version, game_room.snapshot(),
        white_name=game_room.player_name("white"), black_name=game_room.player_name("black"),
    ))
