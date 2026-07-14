from model.position import Position
from state.game_events import MoveAccepted, PieceCaptured
from ui_components.score_panel import ScorePanel


def test_starts_at_zero_zero():
    panel = ScorePanel()
    assert panel.white_score == 0
    assert panel.black_score == 0
    assert panel.summary() == "White: 0   Black: 0"


def test_white_capture_increments_white_score():
    panel = ScorePanel()
    panel.handle_event(PieceCaptured(position=Position(4, 3), captured_token="bP", by_token="wR"))
    assert panel.white_score == 1
    assert panel.black_score == 0


def test_black_capture_increments_black_score():
    panel = ScorePanel()
    panel.handle_event(PieceCaptured(position=Position(4, 3), captured_token="wP", by_token="bR"))
    assert panel.black_score == 1
    assert panel.white_score == 0


def test_capture_with_unknown_capturer_is_not_credited_to_either_side():
    panel = ScorePanel()
    panel.handle_event(PieceCaptured(position=Position(4, 3), captured_token="wB", by_token=None))
    assert panel.white_score == 0
    assert panel.black_score == 0


def test_non_capture_events_are_ignored():
    panel = ScorePanel()
    panel.handle_event(MoveAccepted(source=Position(0, 0), destination=Position(0, 1), token="wR"))
    assert panel.white_score == 0
    assert panel.black_score == 0
