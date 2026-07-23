"""Unit coverage for message_router (server/router/message_router.py) -
routing a decoded message to the handler registered for its type. Each
handler's own behavior is covered where it lives (test_handlers.py); this
only checks that dispatch reaches the right one, that an unregistered type
gets a clean error instead of a KeyError, and that build_router wires every
client message type to something callable.
"""

import json

import protocol
from router import message_router


class FakeSocket:
    def __init__(self):
        self.sent = []

    async def send(self, text: str) -> None:
        self.sent.append(json.loads(text))


class FakeConnection:
    def __init__(self):
        self.socket = FakeSocket()

    async def send(self, message: dict) -> None:
        await self.socket.send(protocol.encode(message))


async def test_dispatch_routes_to_the_handler_registered_for_the_message_type():
    calls = []

    async def handler(connection, message):
        calls.append((connection, message))

    router = {"some_type": handler}
    connection = FakeConnection()
    message = {"type": "some_type"}

    await message_router.dispatch(router, connection, message)

    assert calls == [(connection, message)]


async def test_dispatch_sends_bad_message_for_an_unregistered_type():
    connection = FakeConnection()
    await message_router.dispatch({}, connection, {"type": "no_such_type"})
    assert connection.socket.sent[-1]["type"] == protocol.ERROR
    assert connection.socket.sent[-1]["code"] == "bad_message"


def test_build_router_wires_every_client_to_server_message_type_to_a_handler():
    router = message_router.build_router(matchmaking=object(), rooms=object(), games=object(), users=object())
    expected_types = {
        protocol.LOGIN, protocol.PLAY, protocol.CANCEL_MATCHMAKING, protocol.REJOIN_GAME,
        protocol.LIST_ROOMS, protocol.CREATE_ROOM, protocol.JOIN_ROOM, protocol.CANCEL_ROOM,
        protocol.WATCH_ROOM, protocol.REQUEST_MOVE, protocol.REQUEST_JUMP,
    }
    assert set(router) == expected_types
    assert all(callable(handler) for handler in router.values())
