"""Owns pending-motion bookkeeping for GameFacade: predicting where an
in-flight piece should be drawn, and translating GameEngine.wait()'s
resolved outcomes into the state/game_events.py types log/score panels
subscribe to.

Split out of GameFacade so GameFacade itself only has to coordinate the
engine + this tracker + the event stream, instead of also being the one
holding and mutating the pending-motion dict directly.
"""

from engine.game_engine import Arrived, Captured, Halted, Promoted

from state.game_events import PieceArrived, PieceCaptured, PieceHalted, Promotion


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


class MotionTracker:
    """Pure bookkeeping - no Subject/publish dependency, so it's testable with
    plain outcome objects in, translated event list out."""

    def __init__(self):
        self._pending: dict = {}

    def start(self, source, destination, token: str, duration_ms: float, is_jump: bool) -> None:
        self._pending[source] = PendingMotion(source, destination, token, duration_ms, is_jump)

    def pending(self) -> dict:
        """Read-only view of in-flight motions, keyed by their source cell."""
        return dict(self._pending)

    def advance_all(self, dt_ms: int) -> None:
        for motion in self._pending.values():
            motion.advance(dt_ms)

    def resolve(self, outcomes) -> list:
        """Drop the pending motion each engine outcome resolved (if any - an
        outcome may come from a motion this tracker never tracked, e.g. one
        started directly on the engine), and return the matching UI events."""
        events = []
        for outcome in outcomes:
            self._pending.pop(outcome.source, None)
            events.append(_translate(outcome))
        return events


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
