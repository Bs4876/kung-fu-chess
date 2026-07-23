"""Unit coverage for Gateway (server/gateway/ws_server.py) - the read loop,
JSON decoding, exception containment around dispatch, and disconnect
cleanup. Which handler a message reaches is message_router's own concern
(test_message_router.py); a minimal fake router here keeps that out of
scope so a failure here is unambiguous. Real-socket end-to-end coverage
stays in server/tests/integration/test_ws_integration.py and
test_full_flow.py.
"""

import json

import protocol
from gateway.ws_server import Gateway


class FakeSocket:
    """Records what's sent to it, decoded back to a dict - same shape as
    test_game_service.py's own FakeSocket."""

    def __init__(self):
        self.sent = []

    async def send(self, text: str) -> None:
        self.sent.append(json.loads(text))


class FakeIterableSocket(FakeSocket):
    """Adds async iteration over a fixed list of already-encoded inbound
    messages, then stops - standing in for a real connection that closes
    right after sending them, for testing Gateway.run()'s loop."""

    def __init__(self, messages: list[str]):
        super().__init__()
        self._messages = iter(messages)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._messages)
        except StopIteration:
            raise StopAsyncIteration


class FakeMatchmaking:
    """Stands in for services/matchmaking_service.py's Matchmaking: Gateway.run()
    calls cancel() unconditionally on every disconnect, bypassing dispatch
    entirely, so that's all this needs to record."""

    def __init__(self):
        self.cancelled: list = []

    def cancel(self, websocket) -> None:
        self.cancelled.append(websocket)


class FakeRoom:
    """Stands in for a GameRoom: Gateway.run()'s cleanup only ever calls
    leave()/leave_viewer() on whatever's seated in connection.room/
    viewing_room, so that's all this records."""

    def __init__(self):
        self.left: list = []
        self.left_viewers: list = []

    def leave(self, socket) -> None:
        self.left.append(socket)

    def leave_viewer(self, socket) -> None:
        self.left_viewers.append(socket)


async def failing_handler(connection, message) -> None:
    raise ValueError("boom")


def gateway_for(router: dict | None = None, matchmaking=None):
    socket = FakeSocket()
    gateway = Gateway(socket, router or {}, matchmaking or FakeMatchmaking())
    return gateway, socket


async def test_dispatch_sends_an_error_for_malformed_json():
    gateway, socket = gateway_for()
    await gateway.dispatch("not valid json")
    assert socket.sent[-1]["type"] == protocol.ERROR
    assert socket.sent[-1]["code"] == "bad_message"


async def test_dispatch_recovers_when_a_handler_raises():
    # A well-formed-but-malformed message (e.g. request_move missing
    # "source") or any other bug in a single handler must not take the
    # connection down.
    gateway, socket = gateway_for(router={"boom": failing_handler})
    await gateway.dispatch(protocol.encode({"type": "boom"}))
    assert socket.sent[-1]["type"] == protocol.ERROR
    assert socket.sent[-1]["code"] == "bad_message"


async def test_run_cleans_up_matchmaking_room_and_viewer_state_on_disconnect():
    matchmaking = FakeMatchmaking()
    socket = FakeIterableSocket([])
    gateway = Gateway(socket, {}, matchmaking)
    room = FakeRoom()
    viewing_room = FakeRoom()
    gateway.connection.room = room
    gateway.connection.viewing_room = viewing_room

    await gateway.run()

    assert socket in matchmaking.cancelled
    assert socket in room.left
    assert socket in viewing_room.left_viewers
