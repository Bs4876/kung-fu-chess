"""Wraps GameEngine to add client-side motion prediction and event notifications.

The engine only ever shows a piece "resting at source" or "resting at
destination" (see server/realtime/motion.py - mid-flight positions exist only
for the arbiter's own collision math and are never exposed via GameSnapshot).
Smooth in-flight animation is therefore a client-side prediction (see
PendingMotion), advanced every tick independently of the engine's own timing.

What actually happened to a motion (arrival, capture, halt, promotion) is
never guessed at client-side, though: GameEngine.wait() already knows this
with certainty the instant it happens, and returns it directly (see
engine/game_engine.py's Arrived/Captured/Halted/Promoted). _resolve_outcomes
just translates each one into the matching state/game_events.py type that
log/score panels subscribe to.
"""

from engine.game_engine import Arrived, Captured, Halted, Promoted
from config import JUMP_TRAVEL_TIME, MOVE_TRAVEL_TIME_PER_CELL
from model.board import EMPTY

from state.game_events import (
    GameOver, MoveAccepted, MoveRejected, PieceArrived, PieceCaptured, PieceHalted, Promotion,
)
from state.observer import Subject


def _chebyshev_distance(a, b) -> int:
    return max(abs(a.row - b.row), abs(a.col - b.col))


class PendingMotion:
    """A piece's predicted travel from source to destination, for animation only.

    Timed with the exact same constants the server itself uses (imported, never
    re-derived), so the predicted pixel motion tracks the real one closely. Its
    resolution (arrival/capture/halt/promotion) is never guessed from this -
    that comes straight from GameEngine.wait()'s return value instead.
    """

    def __init__(self, source, destination, token: str, duration_ms: float, is_jump: bool):
        self.source = source
        self.destination = destination
        self.token = token
        self.duration_ms = duration_ms
        self.is_jump = is_jump
        self.elapsed_ms = 0.0

    def advance(self, dt_ms: int) -> None:
        self.elapsed_ms += dt_ms

    @property
    def progress(self) -> float:
        """0.0 at the start of the motion, 1.0 once predicted to have arrived."""
        if self.duration_ms <= 0:
            return 1.0
        return min(self.elapsed_ms / self.duration_ms, 1.0)


class GameFacade:
    """Adds pending-motion bookkeeping and an event stream on top of a real
    GameEngine.

    Exposes the same request_move/snapshot shape server's Controller already
    expects, so Controller can point at this instead of the raw engine unmodified.
    """

    def __init__(self, engine):
        self._engine = engine
        self._pending: dict = {}
        self._events = Subject()

    @property
    def game_over(self) -> bool:
        return self._engine.game_over

    def subscribe(self, callback) -> None:
        """Register callback(event) to be notified of MoveAccepted, MoveRejected,
        PieceArrived, PieceCaptured, PieceHalted, Promotion, and GameOver events."""
        self._events.subscribe(callback)

    def snapshot(self):
        return self._engine.snapshot()

    def pending_motions(self) -> dict:
        """Read-only view of in-flight motions, keyed by their source cell."""
        return dict(self._pending)

    def request_move(self, source, destination):
        result = self._engine.request_move(source, destination)
        if result.is_accepted:
            snapshot = self._engine.snapshot()
            token = snapshot.get_piece(source)
            duration_ms = _chebyshev_distance(source, destination) * MOVE_TRAVEL_TIME_PER_CELL
            self._pending[source] = PendingMotion(source, destination, token, duration_ms, is_jump=False)
            self._events.publish(MoveAccepted(source, destination, token))
        else:
            self._events.publish(MoveRejected(source, destination, result.reason))
        return result

    def request_jump(self, source, destination) -> None:
        snapshot = self._engine.snapshot()
        token = snapshot.get_piece(source)
        self._engine.request_jump(source, destination)
        # request_jump has no return value to confirm acceptance; a jump silently
        # ignored by the engine (game over, already moving, out of bounds) just
        # never produces a resolution event from wait() later, so it stays
        # pending harmlessly until this same source is used again.
        if token != EMPTY:
            self._pending[source] = PendingMotion(source, destination, token, JUMP_TRAVEL_TIME, is_jump=True)

    def tick(self, dt_ms: int):
        """Advance the engine's real clock, publishing whatever it reports just
        resolved, and advance predicted motions for animation. Returns the
        fresh snapshot."""
        game_over_before = self._engine.game_over
        outcomes = self._engine.wait(dt_ms)
        curr_snapshot = self._engine.snapshot()

        for motion in self._pending.values():
            motion.advance(dt_ms)
        self._resolve_outcomes(outcomes)

        if curr_snapshot.game_over and not game_over_before:
            self._events.publish(GameOver())
        return curr_snapshot

    def _resolve_outcomes(self, outcomes) -> None:
        """Drop the pending motion each engine outcome resolved (if any - an
        outcome may come from a motion this facade never tracked, e.g. one
        started directly on the engine), and publish the matching UI event."""
        for outcome in outcomes:
            self._pending.pop(outcome.source, None)
            self._events.publish(_translate(outcome))


_TRANSLATORS = {
    Arrived: lambda o: PieceArrived(source=o.source, destination=o.destination, token=o.token, is_jump=o.is_jump),
    Captured: lambda o: PieceCaptured(position=o.position, captured_token=o.captured_token, by_token=o.by_token,
                                       is_jump=o.is_jump),
    Halted: lambda o: PieceHalted(source=o.source, resting_at=o.resting_at, token=o.token, is_jump=o.is_jump),
    Promoted: lambda o: Promotion(position=o.position, from_token=o.from_token, to_token=o.to_token,
                                   is_jump=o.is_jump),
}


def _translate(outcome):
    """Turn one of GameEngine.wait()'s domain outcomes into the matching
    state/game_events.py type that log/score panels actually subscribe to."""
    return _TRANSLATORS[type(outcome)](outcome)
