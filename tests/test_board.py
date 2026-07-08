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
