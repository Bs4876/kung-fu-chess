"""list_rooms / create_room / join_room / cancel_room / watch_room / rejoin_game."""

import protocol
from handlers.common import enter_room, require_authenticated, watch


async def handle_list_rooms(connection, message: dict, rooms) -> None:
    await connection.send(protocol.room_list(rooms.list_rooms()))


async def handle_create_room(connection, message: dict, rooms) -> None:
    if not await require_authenticated(connection):
        return
    room_id = rooms.create_room(message["name"], connection.socket, connection.session.user)
    await connection.send(protocol.room_created(room_id))
    await enter_room(connection, await rooms.await_join(room_id))


async def handle_join_room(connection, message: dict, rooms) -> None:
    if not await require_authenticated(connection):
        return
    room_id = message["room_id"]
    game_room = rooms.join_room(room_id, connection.socket, connection.session.user)
    if game_room is not None:
        await enter_room(connection, game_room)
        return
    # Not joinable as the 2nd player (already running, or never existed) -
    # the same Join action falls back to seating as a viewer if the room
    # is in fact already running, so one button covers both cases
    # (matches the course spec's single Join action - see
    # services/room_service.py's own docstring).
    game_room = rooms.watch_room(room_id)
    if game_room is None:
        await connection.send(protocol.error("cannot_join_room", "room not found"))
        return
    await watch(connection, game_room)


async def handle_cancel_room(connection, message: dict, rooms) -> None:
    rooms.cancel_room(message["room_id"], connection.socket)


async def handle_watch_room(connection, message: dict, rooms) -> None:
    if not await require_authenticated(connection):
        return
    game_room = rooms.watch_room(message["room_id"])
    if game_room is None:
        await connection.send(protocol.error("cannot_watch_room", "room not found or not yet running"))
        return
    await watch(connection, game_room)


async def handle_rejoin_game(connection, message: dict, games) -> None:
    # Deliberately no require_authenticated() guard here, unlike every
    # other seating operation above - matches this handler's pre-split
    # behavior exactly (not otherwise a spec requirement).
    target = games.get(message["game_id"])
    color = target.color_of_player(connection.session.user) if target is not None else None
    if target is None or color is None or target.ended:
        await connection.send(protocol.error("cannot_rejoin", "no active game to rejoin"))
        return
    target.rejoin(connection.socket, color)
    await enter_room(connection, target)
