import pytest
from chess_io.board_parser import BoardParser
from model.board import EMPTY


def parse(text):
    return BoardParser().parse(text)


def test_single_row_board():
    b = parse("wK . bK")
    assert b.rows == 1
    assert b.cols == 3


def test_multi_row_board_dimensions():
    b = parse("wK . .\n. . .\n. . bK")
    assert b.rows == 3
    assert b.cols == 3


def test_empty_cell_parsed_as_empty():
    b = parse(". . .")
    from model.position import Position
    assert b.get_piece(Position(0, 0)) == EMPTY


def test_piece_token_parsed_correctly():
    b = parse("wR . bK")
    from model.position import Position
    assert b.get_piece(Position(0, 0)) == "wR"
    assert b.get_piece(Position(0, 2)) == "bK"


def test_all_piece_kinds_accepted():
    b = parse("wK wQ wR wB wN wP")
    assert b.cols == 6


def test_raises_on_empty_text():
    with pytest.raises(ValueError, match="Empty board definition"):
        parse("")


def test_raises_on_whitespace_only():
    with pytest.raises(ValueError, match="Empty board definition"):
        parse("   \n  ")


def test_raises_on_inconsistent_row_length():
    with pytest.raises(ValueError, match="Inconsistent"):
        parse("wK . .\n. bK")


def test_raises_on_invalid_token():
    with pytest.raises(ValueError, match="Invalid token"):
        parse("wK xZ")


def test_raises_on_invalid_color():
    with pytest.raises(ValueError, match="Invalid token"):
        parse("xK . .")


def test_raises_on_invalid_kind():
    with pytest.raises(ValueError, match="Invalid token"):
        parse("wX . .")


def test_whitespace_lines_ignored():
    b = parse("\nwK . .\n\n. . .\n")
    assert b.rows == 2
