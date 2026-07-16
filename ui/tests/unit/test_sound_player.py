import winsound

import ui_config
from model.position import Position
from state.game_events import GameOver, MoveAccepted, MoveRejected, PieceCaptured, PieceHalted, Promotion
from ui_components.sound_player import SoundPlayer


def played_paths(monkeypatch):
    calls = []
    monkeypatch.setattr(winsound, "PlaySound", lambda path, flags: calls.append(path))
    return calls


def test_move_accepted_plays_the_move_sound(monkeypatch):
    calls = played_paths(monkeypatch)
    SoundPlayer().handle_event(MoveAccepted(Position(0, 0), Position(0, 1), "wP"))
    assert calls == [str(ui_config.SOUND_MOVE)]


def test_move_rejected_plays_the_illegal_move_sound(monkeypatch):
    calls = played_paths(monkeypatch)
    SoundPlayer().handle_event(MoveRejected(Position(0, 0), Position(0, 1), "not a legal move"))
    assert calls == [str(ui_config.SOUND_ILLEGAL_MOVE)]


def test_piece_captured_plays_the_capture_sound(monkeypatch):
    calls = played_paths(monkeypatch)
    SoundPlayer().handle_event(PieceCaptured(Position(0, 0), "bP", "wQ"))
    assert calls == [str(ui_config.SOUND_CAPTURE)]


def test_promotion_plays_the_promotion_sound(monkeypatch):
    calls = played_paths(monkeypatch)
    SoundPlayer().handle_event(Promotion(Position(0, 0), "wP", "wQ"))
    assert calls == [str(ui_config.SOUND_PROMOTION)]


def test_game_over_plays_the_game_over_sound(monkeypatch):
    calls = played_paths(monkeypatch)
    SoundPlayer().handle_event(GameOver())
    assert calls == [str(ui_config.SOUND_GAME_OVER)]


def test_unmapped_event_plays_nothing(monkeypatch):
    calls = played_paths(monkeypatch)
    SoundPlayer().handle_event(PieceHalted(Position(0, 0), Position(1, 1), "wB"))
    assert calls == []
