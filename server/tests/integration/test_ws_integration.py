"""One real end-to-end smoke test over an actual socket - proving the asyncio
tick loop, protocol encoding, and GameRoom wiring all work together. Most
protocol/room behavior is covered without a socket in tests/unit/; this file
stays deliberately small.
"""

import asyncio

import pytest
import websockets

from net import protocol
from net.ws_server import serve


@pytest.fixture
async def running_server(tmp_path):
    server = await serve(host="localhost", port=0, log_dir=tmp_path, db_path=tmp_path / "test.db")
    port = server.sockets[0].getsockname()[1]
    yield port
    server.close()
    await server.wait_closed()


async def test_two_clients_join_and_play_a_full_move_over_a_real_socket(running_server):
    uri = f"ws://localhost:{running_server}"

    async with websockets.connect(uri) as white_ws, websockets.connect(uri) as black_ws:
        white_start = protocol.decode(await white_ws.recv())
        black_start = protocol.decode(await black_ws.recv())
        assert {white_start["color"], black_start["color"]} == {"white", "black"}

        await white_ws.send(protocol.encode({
            "type": protocol.REQUEST_MOVE,
            "source": {"row": 6, "col": 0},
            "destination": {"row": 5, "col": 0},
        }))

        accepted = protocol.decode(await white_ws.recv())
        assert accepted["type"] == protocol.MOVE_ACCEPTED

        arrived = protocol.decode(await asyncio.wait_for(white_ws.recv(), timeout=3))
        assert arrived["type"] == protocol.ARRIVED
        assert arrived["state_version"] == 1


async def test_a_third_and_fourth_connection_are_paired_into_a_separate_room(running_server):
    uri = f"ws://localhost:{running_server}"

    async with websockets.connect(uri) as first, websockets.connect(uri) as second, \
            websockets.connect(uri) as third, websockets.connect(uri) as fourth:
        first_room = protocol.decode(await first.recv())["game_id"]
        second_room = protocol.decode(await second.recv())["game_id"]
        third_room = protocol.decode(await third.recv())["game_id"]
        fourth_room = protocol.decode(await fourth.recv())["game_id"]

        assert first_room == second_room
        assert third_room == fourth_room
        assert first_room != third_room


async def test_register_then_login_over_a_real_socket(running_server):
    uri = f"ws://localhost:{running_server}"

    # AnonymousLobby.join() blocks a lone connection until a second one
    # pairs with it (see net/anonymous_lobby.py) - _opponent exists purely
    # to unblock that pairing so ws gets its game_start and the dispatch
    # loop (where login/register are handled) actually starts.
    async with websockets.connect(uri) as ws, websockets.connect(uri) as _opponent:
        await ws.recv()  # game_start - not what this test cares about

        await ws.send(protocol.encode(protocol.register("alice", "hunter2")))
        register_response = protocol.decode(await ws.recv())
        assert register_response["success"] is True
        assert register_response["username"] == "alice"

        await ws.send(protocol.encode(protocol.login("alice", "wrong password")))
        failed_login = protocol.decode(await ws.recv())
        assert failed_login["success"] is False

        await ws.send(protocol.encode(protocol.login("alice", "hunter2")))
        ok_login = protocol.decode(await ws.recv())
        assert ok_login["success"] is True
        assert ok_login["elo"] == register_response["elo"]
