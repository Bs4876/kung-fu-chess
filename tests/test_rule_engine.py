from model.board import Board, EMPTY
from model.position import Position
from rules.rule_engine import RuleEngine


def board_from(rows):
    return Board([[c for c in row.split()] for row in rows])


engine = RuleEngine()


def test_valid_move_returns_ok():
    b = board_from(["wR . .", ". . .", ". . ."])
    result = engine.validate_move(b, Position(0, 0), Position(0, 2))
    assert result.is_valid
    assert result.reason == "ok"


def test_outside_board_source():
    b = board_from(["wR . .", ". . .", ". . ."])
    result = engine.validate_move(b, Position(9, 9), Position(0, 0))
    assert not result.is_valid
    assert result.reason == "outside_board"


def test_outside_board_destination():
    b = board_from(["wR . .", ". . .", ". . ."])
    result = engine.validate_move(b, Position(0, 0), Position(9, 9))
    assert not result.is_valid
    assert result.reason == "outside_board"


def test_empty_source():
    b = board_from(["wR . .", ". . .", ". . ."])
    result = engine.validate_move(b, Position(0, 1), Position(0, 2))
    assert not result.is_valid
    assert result.reason == "empty_source"


def test_friendly_destination():
    b = board_from(["wR wP .", ". . .", ". . ."])
    result = engine.validate_move(b, Position(0, 0), Position(0, 1))
    assert not result.is_valid
    assert result.reason == "friendly_destination"


def test_illegal_piece_move():
    b = board_from(["wR . .", ". . .", ". . ."])
    result = engine.validate_move(b, Position(0, 0), Position(1, 1))
    assert not result.is_valid
    assert result.reason == "illegal_piece_move"


def test_capture_enemy_is_valid():
    b = board_from(["wR . bP", ". . .", ". . ."])
    result = engine.validate_move(b, Position(0, 0), Position(0, 2))
    assert result.is_valid


def test_blocked_path_is_invalid():
    b = board_from(["wR bP bK", ". . .", ". . ."])
    result = engine.validate_move(b, Position(0, 0), Position(0, 2))
    assert not result.is_valid
    assert result.reason == "illegal_piece_move"
