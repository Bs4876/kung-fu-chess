from engine.game_engine import Arrived, Captured, Halted, Promoted
from model.position import Position
from state.game_events import PieceArrived, PieceCaptured, PieceHalted, Promotion
from state.motion_tracker import MotionTracker


def test_starts_with_no_pending_motions():
    tracker = MotionTracker()
    assert tracker.pending() == {}


def test_start_adds_a_pending_motion_keyed_by_source():
    tracker = MotionTracker()
    tracker.start(Position(0, 0), Position(0, 3), "wR", duration_ms=3000, is_jump=False)
    pending = tracker.pending()
    assert list(pending.keys()) == [Position(0, 0)]
    motion = pending[Position(0, 0)]
    assert motion.destination == Position(0, 3)
    assert motion.token == "wR"
    assert motion.duration_ms == 3000
    assert not motion.is_jump


def test_advance_all_progresses_every_pending_motion():
    tracker = MotionTracker()
    tracker.start(Position(0, 0), Position(0, 2), "wR", duration_ms=2000, is_jump=False)
    tracker.advance_all(1000)
    assert tracker.pending()[Position(0, 0)].progress == 0.5


def test_advance_all_drops_a_motion_never_reconciled_once_its_progress_completes():
    # e.g. a jump the engine silently rejected: GameFacade starts the pending
    # motion optimistically and it's never resolved, so without expiry it
    # would sit here forever frozen at progress 1.0 - drawn permanently at its
    # predicted destination pixel, a ghost duplicate of whatever piece is
    # actually there.
    tracker = MotionTracker()
    tracker.start(Position(0, 0), Position(0, 2), "wR", duration_ms=1000, is_jump=True)
    tracker.advance_all(999)
    assert Position(0, 0) in tracker.pending()
    tracker.advance_all(2)
    assert tracker.pending() == {}


def test_resolve_pops_the_matching_pending_motion():
    tracker = MotionTracker()
    tracker.start(Position(0, 0), Position(0, 3), "wR", duration_ms=3000, is_jump=False)
    tracker.resolve([Arrived(Position(0, 0), Position(0, 3), "wR")])
    assert tracker.pending() == {}


def test_resolve_on_an_unmatched_source_is_a_safe_no_op_pop():
    tracker = MotionTracker()
    tracker.start(Position(0, 0), Position(0, 3), "wR", duration_ms=3000, is_jump=False)
    tracker.resolve([Arrived(Position(5, 5), Position(5, 6), "bN")])
    assert Position(0, 0) in tracker.pending()


def test_resolve_translates_arrived():
    tracker = MotionTracker()
    events = tracker.resolve([Arrived(Position(0, 0), Position(0, 3), "wR", is_jump=True)])
    assert events == [PieceArrived(source=Position(0, 0), destination=Position(0, 3), token="wR", is_jump=True)]


def test_resolve_translates_captured():
    tracker = MotionTracker()
    events = tracker.resolve([Captured(Position(0, 0), Position(0, 3), "bN", "wR")])
    assert events == [PieceCaptured(position=Position(0, 3), captured_token="bN", by_token="wR")]


def test_resolve_translates_halted():
    tracker = MotionTracker()
    events = tracker.resolve([Halted(Position(2, 0), Position(1, 1), "wB")])
    assert events == [PieceHalted(source=Position(2, 0), resting_at=Position(1, 1), token="wB")]


def test_resolve_translates_promoted():
    tracker = MotionTracker()
    events = tracker.resolve([Promoted(Position(1, 0), Position(0, 0), "wP", "wQ")])
    assert events == [Promotion(position=Position(0, 0), from_token="wP", to_token="wQ")]


def test_resolve_handles_a_mixed_batch_in_order():
    tracker = MotionTracker()
    tracker.start(Position(0, 0), Position(0, 3), "wR", duration_ms=3000, is_jump=False)
    tracker.start(Position(1, 0), Position(0, 0), "wP", duration_ms=1000, is_jump=False)
    events = tracker.resolve([
        Arrived(Position(0, 0), Position(0, 3), "wR"),
        Promoted(Position(1, 0), Position(0, 0), "wP", "wQ"),
    ])
    assert events == [
        PieceArrived(source=Position(0, 0), destination=Position(0, 3), token="wR"),
        Promotion(position=Position(0, 0), from_token="wP", to_token="wQ"),
    ]
    assert tracker.pending() == {}
