import random

from engine.game_engine import GameSnapshot
from model.board import Board
from model.position import Position
from net import protocol
from net.bot_player import BotPlayer


class FakeRoom:
    def __init__(self, board: Board, legal_by_source: dict | None = None):
        self._board = board
        self._legal_by_source = legal_by_source or {}
        self.requested_moves: list[dict] = []

    def snapshot(self) -> GameSnapshot:
        return GameSnapshot(self._board, game_over=False)

    def legal_destinations(self, source: Position) -> set:
        return self._legal_by_source.get(source, set())

    def handle_request_move(self, message: dict) -> None:
        self.requested_moves.append(message)


def board_from(rows):
    return Board([row.split() for row in rows])


def test_take_turn_does_nothing_when_no_legal_moves_exist():
    room = FakeRoom(board_from(["wR . .", ". . .", ". . ."]))
    bot = BotPlayer(room, "white")
    bot.take_turn()
    assert room.requested_moves == []


def test_take_turn_requests_one_of_its_own_pieces_legal_moves():
    board = board_from(["wR . .", ". . .", ". . ."])
    legal = {Position(0, 0): {Position(0, 1), Position(0, 2)}}
    room = FakeRoom(board, legal)
    bot = BotPlayer(room, "white", rng=random.Random(0))

    bot.take_turn()

    assert len(room.requested_moves) == 1
    message = room.requested_moves[0]
    assert message["source"] == protocol.position_to_wire(Position(0, 0))
    assert protocol.position_from_wire(message["destination"]) in legal[Position(0, 0)]


def test_white_bot_never_moves_a_black_piece():
    board = board_from(["wR . bR", ". . .", ". . ."])
    legal = {
        Position(0, 0): {Position(0, 1)},
        Position(0, 2): {Position(1, 2)},  # black's piece - must never be chosen for a "white" bot
    }
    room = FakeRoom(board, legal)
    bot = BotPlayer(room, "white", rng=random.Random(0))

    bot.take_turn()

    message = room.requested_moves[0]
    assert protocol.position_from_wire(message["source"]) == Position(0, 0)


def test_black_bot_never_moves_a_white_piece():
    board = board_from(["wR . bR", ". . .", ". . ."])
    legal = {
        Position(0, 0): {Position(0, 1)},
        Position(0, 2): {Position(1, 2)},
    }
    room = FakeRoom(board, legal)
    bot = BotPlayer(room, "black", rng=random.Random(0))

    bot.take_turn()

    message = room.requested_moves[0]
    assert protocol.position_from_wire(message["source"]) == Position(0, 2)


def test_empty_cells_are_never_picked_as_a_source():
    board = board_from(["wR . .", ". . .", ". . ."])
    # No legal_by_source entries for empty cells - if the bot ever iterated
    # them as a "piece" it would KeyError/crash rather than just skip them.
    room = FakeRoom(board)
    bot = BotPlayer(room, "white", rng=random.Random(0))
    bot.take_turn()  # must not raise
    assert room.requested_moves == []
