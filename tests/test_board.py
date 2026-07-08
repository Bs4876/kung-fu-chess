import pytest
from constants import EMPTY_CELL
from board import Board


@pytest.fixture
def standard_board():
    matrix = [
        ['wK', 'bQ', EMPTY_CELL],
        [EMPTY_CELL, 'wP', 'bR'],
    ]
    return Board(matrix)


def test_get_piece(standard_board):
    assert standard_board.get_piece(0, 0) == 'wK'
    assert standard_board.get_piece(0, 2) == EMPTY_CELL
    assert standard_board.get_piece(1, 1) == 'wP'
    assert standard_board.get_piece(1, 2) == 'bR'


def test_is_in_bounds(standard_board):
    assert standard_board.is_in_bounds(0, 0)
    assert standard_board.is_in_bounds(1, 1)
    assert not standard_board.is_in_bounds(-1, 0)
    assert not standard_board.is_in_bounds(2, 1)
    assert not standard_board.is_in_bounds(0, 3)


def test_is_empty(standard_board):
    assert standard_board.is_empty(0, 2)
    assert standard_board.is_empty(1, 0)
    assert not standard_board.is_empty(0, 0)
    assert not standard_board.is_empty(1, 2)


def test_set_piece_updates_board_state_and_rows_cols(standard_board):
    standard_board.set_piece(0, 2, 'bP')

    assert standard_board.get_piece(0, 2) == 'bP'
    assert standard_board.rows == 2
    assert standard_board.cols == 3


def test_board_constructor_rejects_invalid_matrix_inputs():
    with pytest.raises(ValueError):
        Board(None)

    with pytest.raises(ValueError):
        Board([[EMPTY_CELL, EMPTY_CELL], [EMPTY_CELL]])


def test_board_accessors_raise_for_out_of_bounds_positions(standard_board):
    with pytest.raises(IndexError):
        standard_board.get_piece(2, 0)

    with pytest.raises(IndexError):
        standard_board.set_piece(2, 0, 'wP')
