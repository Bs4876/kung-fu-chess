from model.position import Position
from state.game_events import GameOver, MoveAccepted, MoveRejected, PieceArrived, PieceCaptured, PieceHalted, Promotion
from ui_components.moves_log_panel import MovesLogPanel


def test_move_accepted_is_logged_with_side_and_cell_names():
    panel = MovesLogPanel()
    panel.handle_event(MoveAccepted(source=Position(6, 4), destination=Position(4, 4), token="wP"))
    assert panel.lines() == ["White P e2-e4"]


def test_black_move_is_attributed_to_black():
    panel = MovesLogPanel()
    panel.handle_event(MoveAccepted(source=Position(1, 4), destination=Position(3, 4), token="bP"))
    assert panel.lines() == ["Black P e7-e5"]


def test_capture_with_a_known_capturer_names_it():
    panel = MovesLogPanel()
    panel.handle_event(PieceCaptured(position=Position(4, 3), captured_token="bP", by_token="wR"))
    assert panel.lines() == ["White R captures bP at d4"]


def test_capture_with_no_known_capturer_still_logs_something_useful():
    panel = MovesLogPanel()
    panel.handle_event(PieceCaptured(position=Position(4, 3), captured_token="wB", by_token=None))
    assert panel.lines() == ["wB destroyed at d4"]


def test_promotion_is_logged():
    panel = MovesLogPanel()
    panel.handle_event(Promotion(position=Position(0, 0), from_token="wP", to_token="wQ"))
    assert panel.lines() == ["White promotes to Q at a8"]


def test_game_over_is_logged():
    panel = MovesLogPanel()
    panel.handle_event(GameOver())
    assert panel.lines() == ["Game Over"]


def test_move_rejected_and_piece_halted_are_not_logged():
    panel = MovesLogPanel()
    panel.handle_event(MoveRejected(source=Position(0, 0), destination=Position(0, 1), reason="illegal_piece_move"))
    panel.handle_event(PieceHalted(source=Position(2, 0), resting_at=Position(1, 1), token="wB"))
    assert panel.lines() == []


def test_piece_arrived_is_not_logged_separately_from_its_move_accepted():
    panel = MovesLogPanel()
    panel.handle_event(PieceArrived(source=Position(0, 0), destination=Position(0, 3), token="wR"))
    assert panel.lines() == []


def test_lines_are_most_recent_first():
    panel = MovesLogPanel()
    panel.handle_event(MoveAccepted(source=Position(6, 4), destination=Position(4, 4), token="wP"))
    panel.handle_event(MoveAccepted(source=Position(1, 4), destination=Position(3, 4), token="bP"))
    assert panel.lines() == ["Black P e7-e5", "White P e2-e4"]
