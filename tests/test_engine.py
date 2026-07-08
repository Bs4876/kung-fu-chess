import pytest

from board import Board
from constants import BLACK, EMPTY_CELL, JUMP_TRAVEL_TIME, MOVE_TRAVEL_TIME, WHITE
from engine import ChessEngine


@pytest.fixture
def empty_board():
    return Board([[EMPTY_CELL for _ in range(8)] for _ in range(8)])


def test_click_adds_valid_move_to_ongoing_moves(empty_board):
    empty_board.set_piece(7, 3, WHITE + 'P')

    engine = ChessEngine(empty_board)

    engine.click(300, 700)
    engine.click(300, 600)

    assert len(engine.ongoing_moves) == 1
    assert engine.ongoing_moves[0][0] == MOVE_TRAVEL_TIME
    assert engine.ongoing_moves[0][1:5] == (7, 3, 6, 3)
    assert engine.ongoing_moves[0][5] == WHITE + 'P'
    assert engine.selected_pos is None


def test_execute_jump_records_arrival_time_from_constants(empty_board):
    empty_board.set_piece(0, 0, WHITE + 'P')

    engine = ChessEngine(empty_board)
    engine._execute_jump(0, 0)

    assert len(engine.ongoing_jumps) == 1
    assert engine.ongoing_jumps[0][0] == JUMP_TRAVEL_TIME
    assert engine.ongoing_jumps[0][1:] == (0, 0, WHITE + 'P')


def test_invalid_click_is_ignored_without_mutating_state(empty_board):
    engine = ChessEngine(empty_board)

    engine.click(10000, 10000)

    assert engine.ongoing_moves == []
    assert engine.ongoing_jumps == []
    assert engine.selected_pos is None


def test_refresh_board_state_clears_expired_moves(empty_board):
    empty_board.set_piece(7, 3, WHITE + 'P')

    engine = ChessEngine(empty_board)
    engine.ongoing_moves.append((MOVE_TRAVEL_TIME, 7, 3, 6, 3, WHITE + 'P'))
    engine.pieces_in_flight.add((7, 3))
    engine.game_clock = MOVE_TRAVEL_TIME

    engine._refresh_board_state()

    assert engine.ongoing_moves == []
    assert (7, 3) not in engine.pieces_in_flight
    assert empty_board.get_piece(6, 3) == WHITE + 'P'
    assert empty_board.get_piece(7, 3) == EMPTY_CELL


def test_click_selects_same_color_piece_and_rejects_out_of_bounds(empty_board):
    empty_board.set_piece(0, 0, WHITE + 'P')
    empty_board.set_piece(0, 1, WHITE + 'N')

    engine = ChessEngine(empty_board)
    engine.click(0, 0)
    engine.click(100, 0)
    engine.click(10000, 10000)

    assert engine.selected_pos == (0, 1)


def test_click_executes_jump_when_same_cell_is_reselected(empty_board):
    empty_board.set_piece(0, 0, WHITE + 'P')

    engine = ChessEngine(empty_board)
    engine.click(0, 0)
    engine.click(0, 0)
    assert len(engine.ongoing_jumps) == 1

    empty_board.set_piece(0, 0, EMPTY_CELL)
    engine.selected_pos = (0, 0)
    engine.click(0, 0)
    assert len(engine.ongoing_jumps) == 1


def test_click_attempts_move_against_a_different_color_piece(empty_board):
    empty_board.set_piece(0, 0, WHITE + 'P')
    empty_board.set_piece(0, 1, BLACK + 'P')

    engine = ChessEngine(empty_board)
    engine.click(0, 0)
    engine.click(100, 0)

    assert engine.ongoing_moves == []


def test_execute_move_rejects_enemy_moves_and_invalid_targets(empty_board):
    empty_board.set_piece(7, 3, WHITE + 'P')
    empty_board.set_piece(6, 3, WHITE + 'N')

    engine = ChessEngine(empty_board)
    engine.ongoing_moves.append((MOVE_TRAVEL_TIME, 0, 0, 0, 1, BLACK + 'P'))

    engine._execute_move(7, 3, 6, 3)
    assert len(engine.ongoing_moves) == 1

    engine._execute_move(7, 3, 7, 4)
    assert len(engine.ongoing_moves) == 1


def test_refresh_board_state_handles_airborne_collision_and_promotion(empty_board):
    empty_board.set_piece(7, 3, WHITE + 'P')
    empty_board.set_piece(6, 3, BLACK + 'P')

    engine = ChessEngine(empty_board)
    engine.ongoing_jumps.append((JUMP_TRAVEL_TIME, 0, 0, BLACK + 'P'))
    engine.ongoing_moves.append((MOVE_TRAVEL_TIME, 7, 3, 0, 0, WHITE + 'P'))
    engine.pieces_in_flight.add((7, 3))

    engine._refresh_board_state()

    assert empty_board.get_piece(7, 3) == EMPTY_CELL
    assert (7, 3) not in engine.pieces_in_flight


def test_refresh_board_state_promotes_pawn_and_captures_king(empty_board):
    empty_board.set_piece(6, 0, WHITE + 'P')
    empty_board.set_piece(0, 0, BLACK + 'K')

    engine = ChessEngine(empty_board)
    engine.ongoing_moves.append((0, 6, 0, 0, 0, WHITE + 'P'))
    engine.pieces_in_flight.add((6, 0))
    engine.game_clock = 0

    engine._refresh_board_state()

    assert engine.game_over is True
    assert empty_board.get_piece(0, 0) == WHITE + 'Q'
    assert engine.ongoing_moves == []


def test_execute_move_returns_when_game_is_over(empty_board):
    empty_board.set_piece(7, 3, WHITE + 'P')

    engine = ChessEngine(empty_board)
    engine.game_over = True

    engine._execute_move(7, 3, 6, 3)

    assert engine.ongoing_moves == []


def test_execute_move_returns_when_target_is_friendly(empty_board):
    empty_board.set_piece(7, 3, WHITE + 'P')
    empty_board.set_piece(6, 3, WHITE + 'N')

    engine = ChessEngine(empty_board)
    engine._execute_move(7, 3, 6, 3)

    assert engine.ongoing_moves == []


def test_jump_and_wait_and_print_board_cover_the_remaining_engine_paths(empty_board, capsys):
    empty_board.set_piece(0, 0, WHITE + 'P')

    engine = ChessEngine(empty_board)
    engine.jump(0, 0)
    engine.wait(250)
    engine.print_board()

    captured = capsys.readouterr()
    assert len(engine.ongoing_jumps) == 1
    assert engine.game_clock == 250
    assert "wP" in captured.out


def test_click_is_blocked_when_piece_is_in_flight_or_game_is_over(empty_board):
    empty_board.set_piece(0, 0, WHITE + 'P')

    engine = ChessEngine(empty_board)
    engine.pieces_in_flight.add((0, 0))
    engine.click(0, 0)

    assert engine.selected_pos is None

    engine.game_over = True
    engine.click(100, 0)
    assert engine.selected_pos is None


def test_jump_returns_when_game_is_over_or_out_of_bounds(empty_board):
    engine = ChessEngine(empty_board)
    engine.game_over = True
    engine.jump(0, 0)

    assert engine.ongoing_jumps == []

    engine.game_over = False
    engine.jump(10000, 10000)

    assert engine.ongoing_jumps == []


def test_execute_jump_and_move_return_for_empty_or_in_flight_positions(empty_board):
    engine = ChessEngine(empty_board)
    engine._execute_jump(0, 0)
    assert engine.ongoing_jumps == []

    engine._execute_move(1, 1, 1, 2)
    assert engine.ongoing_moves == []

    empty_board.set_piece(0, 0, WHITE + 'P')
    engine._execute_jump(0, 0)
    engine.pieces_in_flight.add((0, 0))
    engine._execute_jump(0, 0)

    assert len(engine.ongoing_jumps) == 1

    engine._execute_move(0, 0, 0, 1)
    assert engine.ongoing_moves == []

    engine.pieces_in_flight.remove((0, 0))
    engine._execute_move(0, 0, 0, 1)
    assert engine.ongoing_moves == []


def test_refresh_board_state_discards_expired_jumps_and_pending_moves(empty_board):
    empty_board.set_piece(7, 3, WHITE + 'P')
    empty_board.set_piece(6, 3, WHITE + 'N')

    engine = ChessEngine(empty_board)
    engine.ongoing_jumps.append((0, 0, 0, WHITE + 'P'))
    engine.ongoing_moves.append((MOVE_TRAVEL_TIME + 1, 7, 3, 6, 3, WHITE + 'P'))
    engine.pieces_in_flight.add((7, 3))

    engine._refresh_board_state()

    assert engine.ongoing_jumps == []
    assert len(engine.ongoing_moves) == 1


def test_refresh_board_state_discards_moves_when_game_is_over(empty_board):
    empty_board.set_piece(7, 3, WHITE + 'P')

    engine = ChessEngine(empty_board)
    engine.game_over = True
    engine.ongoing_moves.append((0, 7, 3, 6, 3, WHITE + 'P'))
    engine.pieces_in_flight.add((7, 3))

    engine._refresh_board_state()

    assert engine.ongoing_moves == []


def test_refresh_board_state_discards_moves_when_piece_moves_away_or_target_is_friendly(empty_board):
    empty_board.set_piece(7, 3, WHITE + 'P')
    empty_board.set_piece(6, 3, WHITE + 'N')

    engine = ChessEngine(empty_board)
    engine.ongoing_moves.append((0, 7, 3, 6, 3, WHITE + 'P'))
    engine.pieces_in_flight.add((7, 3))
    empty_board.set_piece(7, 3, EMPTY_CELL)

    engine._refresh_board_state()
    assert engine.ongoing_moves == []

    empty_board.set_piece(7, 3, WHITE + 'P')
    empty_board.set_piece(6, 3, WHITE + 'N')
    engine = ChessEngine(empty_board)
    engine.ongoing_moves.append((0, 7, 3, 6, 3, WHITE + 'P'))
    engine.pieces_in_flight.add((7, 3))

    engine._refresh_board_state()
    assert engine.ongoing_moves == []
