import pytest
from model.board import Board, EMPTY
from model.position import Position


def make_board(rows, cols, fill=EMPTY):
    return Board([[fill] * cols for _ in range(rows)])


def test_dimensions():
    b = make_board(3, 4)
    assert b.rows == 3 and b.cols == 4


def test_empty_cell_returns_empty():
    b = make_board(2, 2)
    assert b.get_piece(Position(0, 0)) == EMPTY


def test_set_and_get_piece():
    b = make_board(2, 2)
    b.set_piece(Position(0, 1), "wR")
    assert b.get_piece(Position(0, 1)) == "wR"


def test_set_piece_with_empty_token_succeeds():
    b = make_board(2, 2)
    b.set_piece(Position(0, 0), EMPTY)
    assert b.get_piece(Position(0, 0)) == EMPTY


def test_double_occupancy_raises():
    b = make_board(2, 2)
    b.set_piece(Position(0, 0), "wR")
    with pytest.raises(ValueError):
        b.set_piece(Position(0, 0), "bK")
    assert b.get_piece(Position(0, 0)) == "wR"


def test_in_bounds():
    b = make_board(3, 3)
    assert b.in_bounds(Position(0, 0))
    assert b.in_bounds(Position(2, 2))
    assert not b.in_bounds(Position(3, 0))
    assert not b.in_bounds(Position(0, 3))


def test_get_piece_out_of_bounds_raises():
    b = make_board(2, 2)
    with pytest.raises(IndexError):
        b.get_piece(Position(5, 5))


def test_set_piece_out_of_bounds_raises():
    b = make_board(2, 2)
    with pytest.raises(IndexError):
        b.set_piece(Position(5, 5), "wR")


def test_replace_piece_out_of_bounds_raises():
    b = make_board(2, 2)
    with pytest.raises(IndexError):
        b.replace_piece(Position(5, 5), "wR")


def test_move_piece_updates_src_and_dst():
    b = make_board(3, 3)
    b.set_piece(Position(0, 0), "wR")
    b.move_piece(Position(0, 0), Position(2, 2))
    assert b.get_piece(Position(0, 0)) == EMPTY
    assert b.get_piece(Position(2, 2)) == "wR"


def test_inconsistent_row_length_raises():
    with pytest.raises(ValueError):
        Board([[".", "."], ["."]])


def test_empty_matrix_raises():
    with pytest.raises(ValueError):
        Board([])
