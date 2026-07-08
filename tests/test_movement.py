import pytest
from constants import BLACK, EMPTY_CELL, WHITE
from board import Board
from movement import MoveValidator


@pytest.fixture
def empty_board():
    matrix = [[EMPTY_CELL for _ in range(8)] for _ in range(8)]
    return Board(matrix)


def test_validate_pawn_moves(empty_board):
    # Arrange
    empty_board.set_piece(7, 3, WHITE + 'P')
    empty_board.set_piece(6, 4, BLACK + 'N')

    # Act
    forward_one = MoveValidator._validate_pawn(7, 3, 6, 3, empty_board, WHITE)
    forward_two = MoveValidator._validate_pawn(7, 3, 5, 3, empty_board, WHITE)
    capture_diagonal = MoveValidator._validate_pawn(7, 3, 6, 4, empty_board, WHITE)
    invalid_sideways = MoveValidator._validate_pawn(7, 3, 7, 4, empty_board, WHITE)

    # Assert
    assert forward_one is True
    assert forward_two is True
    assert capture_diagonal is True
    assert invalid_sideways is False


def test_validate_pawn_two_step_blocked(empty_board):
    # Arrange
    empty_board.set_piece(7, 3, WHITE + 'P')
    empty_board.set_piece(6, 3, WHITE + 'N')

    # Act
    blocked_two_step = MoveValidator._validate_pawn(7, 3, 5, 3, empty_board, WHITE)

    # Assert
    assert blocked_two_step is False


def test_validate_knight_moves(empty_board):
    # Arrange
    empty_board.set_piece(4, 4, WHITE + 'N')

    # Act
    valid_l_move = MoveValidator._validate_knight(4, 4, 6, 5, empty_board, WHITE)
    valid_other_l = MoveValidator._validate_knight(4, 4, 5, 6, empty_board, WHITE)
    invalid_move = MoveValidator._validate_knight(4, 4, 5, 5, empty_board, WHITE)

    # Assert
    assert valid_l_move is True
    assert valid_other_l is True
    assert invalid_move is False


def test_validate_king_moves(empty_board):
    # Arrange
    empty_board.set_piece(4, 4, WHITE + 'K')

    # Act
    valid_one_step = MoveValidator._validate_king(4, 4, 5, 5, empty_board, WHITE)
    invalid_two_step = MoveValidator._validate_king(4, 4, 6, 4, empty_board, WHITE)

    # Assert
    assert valid_one_step is True
    assert invalid_two_step is False


def test_validate_rook_moves(empty_board):
    # Arrange
    open_board = Board([[EMPTY_CELL for _ in range(8)] for _ in range(8)])
    open_board.set_piece(3, 3, WHITE + 'R')
    blocked_board = Board([[EMPTY_CELL for _ in range(8)] for _ in range(8)])
    blocked_board.set_piece(3, 3, WHITE + 'R')
    blocked_board.set_piece(3, 5, WHITE + 'P')

    # Act
    valid_horizontal = MoveValidator._validate_rook(3, 3, 3, 7, open_board, WHITE)
    valid_vertical = MoveValidator._validate_rook(3, 3, 0, 3, open_board, WHITE)
    invalid_diagonal = MoveValidator._validate_rook(3, 3, 5, 5, open_board, WHITE)
    blocked_path = MoveValidator._validate_rook(3, 3, 3, 7, blocked_board, WHITE)

    # Assert
    assert valid_horizontal is True
    assert valid_vertical is True
    assert invalid_diagonal is False
    assert blocked_path is False


def test_validate_bishop_moves(empty_board):
    # Arrange
    open_board = Board([[EMPTY_CELL for _ in range(8)] for _ in range(8)])
    open_board.set_piece(2, 2, WHITE + 'B')
    blocked_board = Board([[EMPTY_CELL for _ in range(8)] for _ in range(8)])
    blocked_board.set_piece(2, 2, WHITE + 'B')
    blocked_board.set_piece(3, 3, WHITE + 'P')

    # Act
    valid_diagonal = MoveValidator._validate_bishop(2, 2, 5, 5, open_board, WHITE)
    invalid_straight = MoveValidator._validate_bishop(2, 2, 2, 5, open_board, WHITE)
    blocked_path = MoveValidator._validate_bishop(2, 2, 4, 4, blocked_board, WHITE)

    # Assert
    assert valid_diagonal is True
    assert invalid_straight is False
    assert blocked_path is False


def test_validate_queen_moves(empty_board):
    # Arrange
    open_board = Board([[EMPTY_CELL for _ in range(8)] for _ in range(8)])
    open_board.set_piece(3, 3, WHITE + 'Q')
    blocked_board = Board([[EMPTY_CELL for _ in range(8)] for _ in range(8)])
    blocked_board.set_piece(3, 3, WHITE + 'Q')
    blocked_board.set_piece(3, 5, WHITE + 'P')

    # Act
    valid_straight = MoveValidator._validate_queen(3, 3, 3, 7, open_board, WHITE)
    valid_diagonal = MoveValidator._validate_queen(3, 3, 7, 7, open_board, WHITE)
    invalid_l = MoveValidator._validate_queen(3, 3, 5, 4, open_board, WHITE)
    blocked_path = MoveValidator._validate_queen(3, 3, 3, 7, blocked_board, WHITE)

    # Assert
    assert valid_straight is True
    assert valid_diagonal is True
    assert invalid_l is False
    assert blocked_path is False
