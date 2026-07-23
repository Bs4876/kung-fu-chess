"""Unit coverage for the handlers/ package - one function per client
message type, each translating a message into a call on the relevant
service plus a response back through connection.send(). Each service's
own business logic is tested where it lives (test_auth.py,
test_matchmaking.py, test_room_service.py, test_game_service.py); this
only checks the wiring: auth gating, which service method gets called,
and what gets sent back. Previously reachable only through
ConnectionHandler.route() (see server/tests/integration/
test_ws_integration.py, test_full_flow.py for the end-to-end regression
coverage that stays in place).
"""

import asyncio
import contextlib
import json

from bus.event_bus import EventBus
from model.position import Position
import protocol
from gateway.connection import Connection
from handlers import auth_handler, gameplay_handler, matchmaking_handler, rooms_handler
from services.game_registry import GameRegistry
from services.room_service import RoomRegistry
from persistence.db import connect as connect_db
from persistence.users_repository import UsersRepository


class FakeSocket:
    """Records what's sent to it, decoded back to a dict - same shape as
    test_game_service.py's own FakeSocket."""

    def __init__(self):
        self.sent = []

    async def send(self, text: str) -> None:
        self.sent.append(json.loads(text))


class FakeUser:
    def __init__(self, username: str):
        self.username = username


class FakeMatchmaking:
    """Stands in for services/matchmaking_service.py's Matchmaking: play()
    returns whatever a test presets instead of running the timed pairing
    loop - the handlers only ever await play()'s result and call cancel(),
    they don't care how the result was produced."""

    def __init__(self):
        self.cancelled: list = []
        self.result = None

    async def play(self, websocket, user):
        return self.result

    def cancel(self, websocket) -> None:
        self.cancelled.append(websocket)


def connection_for(tmp_path):
    users = UsersRepository(connect_db(tmp_path / "test.db"))
    bus = EventBus()
    games = GameRegistry(bus)
    rooms = RoomRegistry(games.new_room)
    connection = Connection(FakeSocket())
    return connection, users, games, rooms


async def logged_in_connection(tmp_path):
    connection, users, games, rooms = connection_for(tmp_path)
    await auth_handler.handle_login(connection, protocol.login("alice"), users=users)
    connection.socket.sent.clear()
    return connection, users, games, rooms


# auth_handler

async def test_handle_login_authenticates_the_session_and_returns_a_login_result(tmp_path):
    connection, users, games, rooms = connection_for(tmp_path)

    await auth_handler.handle_login(connection, protocol.login("alice"), users=users)

    assert connection.socket.sent[-1]["type"] == protocol.LOGIN_RESULT
    assert connection.socket.sent[-1]["success"] is True
    assert connection.session.is_authenticated


# matchmaking_handler

async def test_handle_play_before_login_is_rejected(tmp_path):
    connection, users, games, rooms = connection_for(tmp_path)

    await matchmaking_handler.handle_play(connection, protocol.play(), matchmaking=FakeMatchmaking())

    assert connection.socket.sent[-1]["type"] == protocol.ERROR
    assert connection.socket.sent[-1]["code"] == "not_authenticated"


async def test_handle_play_enters_the_room_matchmaking_returns(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)
    matchmaking = FakeMatchmaking()
    room = games.new_room()
    room.join(connection.socket, player=connection.session.user)
    matchmaking.result = room

    await matchmaking_handler.handle_play(connection, protocol.play(), matchmaking=matchmaking)

    assert connection.socket.sent[-1]["type"] == protocol.GAME_START
    assert connection.socket.sent[-1]["color"] == "white"
    assert connection.room is room
    room.stop()


async def test_handle_play_reports_no_opponent_found_when_matchmaking_gives_up(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)

    await matchmaking_handler.handle_play(connection, protocol.play(), matchmaking=FakeMatchmaking())

    assert connection.socket.sent[-1]["type"] == protocol.ERROR
    assert connection.socket.sent[-1]["code"] == "no_opponent_found"


async def test_handle_cancel_matchmaking_cancels_the_connections_socket(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)
    matchmaking = FakeMatchmaking()

    await matchmaking_handler.handle_cancel_matchmaking(connection, protocol.cancel_matchmaking(), matchmaking=matchmaking)

    assert connection.socket in matchmaking.cancelled


# rooms_handler

async def test_handle_create_room_sends_room_created_then_starts_the_game_once_joined(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)

    create_task = asyncio.create_task(rooms_handler.handle_create_room(connection, protocol.create_room("My Room"), rooms=rooms))
    await asyncio.sleep(0)  # let create_room send room_created and start awaiting the 2nd player

    assert connection.socket.sent[-1]["type"] == protocol.ROOM_CREATED
    room_id = connection.socket.sent[-1]["room_id"]

    rooms.join_room(room_id, FakeSocket(), FakeUser("bob"))
    await asyncio.wait_for(create_task, timeout=1)

    assert connection.socket.sent[-1]["type"] == protocol.GAME_START
    assert connection.socket.sent[-1]["color"] == "white"


async def test_handle_join_room_seats_the_second_player(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)
    room_id = rooms.create_room("Alice's room", FakeSocket(), FakeUser("creator"))

    await rooms_handler.handle_join_room(connection, protocol.join_room(room_id), rooms=rooms)

    assert connection.socket.sent[-1]["type"] == protocol.GAME_START
    assert connection.socket.sent[-1]["color"] == "black"


async def test_handle_join_room_falls_back_to_watching_an_already_running_room(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)
    room_id = rooms.create_room("Full room", FakeSocket(), FakeUser("creator"))
    rooms.join_room(room_id, FakeSocket(), FakeUser("joiner"))  # now running/full

    await rooms_handler.handle_join_room(connection, protocol.join_room(room_id), rooms=rooms)

    assert connection.socket.sent[-1]["type"] == protocol.GAME_START
    assert connection.socket.sent[-1]["color"] is None  # viewer, not a seated player


async def test_handle_join_room_with_an_unknown_id_is_rejected(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)

    await rooms_handler.handle_join_room(connection, protocol.join_room("no-such-room"), rooms=rooms)

    assert connection.socket.sent[-1]["type"] == protocol.ERROR
    assert connection.socket.sent[-1]["code"] == "cannot_join_room"


async def test_handle_watch_room_seats_as_a_viewer(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)
    room_id = rooms.create_room("Full room", FakeSocket(), FakeUser("creator"))
    rooms.join_room(room_id, FakeSocket(), FakeUser("joiner"))

    await rooms_handler.handle_watch_room(connection, protocol.watch_room(room_id), rooms=rooms)

    assert connection.socket.sent[-1]["type"] == protocol.GAME_START
    assert connection.socket.sent[-1]["color"] is None


async def test_handle_cancel_room_removes_the_pending_room(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)
    create_task = asyncio.create_task(rooms_handler.handle_create_room(connection, protocol.create_room("My Room"), rooms=rooms))
    await asyncio.sleep(0)
    room_id = connection.socket.sent[-1]["room_id"]

    await rooms_handler.handle_cancel_room(connection, protocol.cancel_room(room_id), rooms=rooms)

    assert rooms.list_rooms() == []
    create_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await create_task


async def test_handle_rejoin_game_reseats_a_previously_disconnected_player(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)
    room = games.new_room()
    room.join(connection.socket, player=connection.session.user)
    room.leave(connection.socket)

    await rooms_handler.handle_rejoin_game(connection, protocol.rejoin_game(room.game_id), games=games)

    assert connection.socket.sent[-1]["type"] == protocol.GAME_START
    assert connection.socket.sent[-1]["color"] == "white"
    room.stop()


async def test_handle_rejoin_game_with_no_matching_game_is_rejected(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)

    await rooms_handler.handle_rejoin_game(connection, protocol.rejoin_game("no-such-game"), games=games)

    assert connection.socket.sent[-1]["type"] == protocol.ERROR
    assert connection.socket.sent[-1]["code"] == "cannot_rejoin"


# gameplay_handler

async def test_handle_request_move_routes_to_the_seated_room(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)
    room = games.new_room()
    room.join(connection.socket, player=connection.session.user)  # seats socket as white
    connection.room = room

    # (6, 0) -> (5, 0): white's own pawn - handle_request_move now checks
    # piece ownership, so this must be a move white can actually make for
    # the routing itself (not ownership) to be what's under test here.
    await gameplay_handler.handle_request_move(connection, protocol.request_move(room.game_id, Position(6, 0), Position(5, 0)))
    await asyncio.sleep(0)  # let GameRoom's fire-and-forget broadcast run

    assert connection.socket.sent[-1]["type"] in (protocol.MOVE_ACCEPTED, protocol.MOVE_REJECTED)
    room.stop()


async def test_handle_request_move_with_no_seated_room_is_rejected(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)

    await gameplay_handler.handle_request_move(connection, protocol.request_move("no-such-game", Position(6, 0), Position(5, 0)))

    assert connection.socket.sent[-1]["type"] == protocol.ERROR
    assert connection.socket.sent[-1]["code"] == "bad_message"


async def test_handle_request_jump_with_no_seated_room_is_rejected(tmp_path):
    connection, users, games, rooms = await logged_in_connection(tmp_path)

    await gameplay_handler.handle_request_jump(connection, protocol.request_jump("no-such-game", Position(6, 0), Position(5, 0)))

    assert connection.socket.sent[-1]["type"] == protocol.ERROR
    assert connection.socket.sent[-1]["code"] == "bad_message"
