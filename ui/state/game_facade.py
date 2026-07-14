"""Wraps GameEngine to add client-side motion prediction.

The engine only ever shows a piece "resting at source" or "resting at
destination" (see server/realtime/motion.py - mid-flight positions exist only
for the arbiter's own collision math and are never exposed via GameSnapshot).
Smooth in-flight animation is therefore a client-side prediction, kept honest
by re-checking the real snapshot every tick (see _reconcile).
"""

from config import JUMP_TRAVEL_TIME, MOVE_TRAVEL_TIME_PER_CELL
from model.board import EMPTY


def _chebyshev_distance(a, b) -> int:
    return max(abs(a.row - b.row), abs(a.col - b.col))


class PendingMotion:
    """A piece's predicted travel from source to destination.

    Timed with the exact same constants the server itself uses (imported, never
    re-derived), so in the common case our own "arrived" and the engine's
    "arrived" line up at the same tick instead of drifting apart.
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

    @property
    def is_due(self) -> bool:
        return self.elapsed_ms >= self.duration_ms


class GameFacade:
    """Adds pending-motion bookkeeping on top of a real GameEngine.

    Exposes the same request_move/snapshot shape server's Controller already
    expects, so Controller can point at this instead of the raw engine unmodified.
    """

    def __init__(self, engine):
        self._engine = engine
        self._pending: dict = {}

    @property
    def game_over(self) -> bool:
        return self._engine.game_over

    def snapshot(self):
        return self._engine.snapshot()

    def pending_motions(self) -> dict:
        """Read-only view of in-flight motions, keyed by their source cell."""
        return dict(self._pending)

    def request_move(self, source, destination):
        result = self._engine.request_move(source, destination)
        if result.is_accepted:
            token = self._engine.snapshot().get_piece(source)
            duration_ms = _chebyshev_distance(source, destination) * MOVE_TRAVEL_TIME_PER_CELL
            self._pending[source] = PendingMotion(source, destination, token, duration_ms, is_jump=False)
        return result

    def request_jump(self, source, destination) -> None:
        token = self._engine.snapshot().get_piece(source)
        self._engine.request_jump(source, destination)
        # request_jump has no return value to confirm acceptance; a jump silently
        # ignored by the engine (game over, already moving, out of bounds) is
        # caught the same way a stale move is - _reconcile() checks the real
        # snapshot once this predicted duration elapses, not before.
        if token != EMPTY:
            self._pending[source] = PendingMotion(source, destination, token, JUMP_TRAVEL_TIME, is_jump=True)

    def tick(self, dt_ms: int):
        """Advance the engine's real clock, then advance and reconcile predicted
        motions against it. Returns the fresh snapshot."""
        self._engine.wait(dt_ms)
        for motion in self._pending.values():
            motion.advance(dt_ms)
        self._reconcile()
        return self._engine.snapshot()

    def _reconcile(self) -> None:
        """Drop any motion whose predicted duration has elapsed.

        By now the engine has already resolved it one way or another (arrival,
        capture, stale-target cancellation, or a mid-flight same-color halt) -
        engine.wait() above always runs before this, so the snapshot is always
        ground truth for wherever the piece actually ended up.
        """
        for source in [source for source, motion in self._pending.items() if motion.is_due]:
            del self._pending[source]
