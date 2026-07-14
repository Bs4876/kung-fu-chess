"""Wraps GameEngine to add client-side motion prediction and event notifications.

The engine only ever shows a piece "resting at source" or "resting at
destination" (see server/realtime/motion.py - mid-flight positions exist only
for the arbiter's own collision math and are never exposed via GameSnapshot).
Smooth in-flight animation is therefore a client-side prediction, kept honest
by re-checking the real snapshot every tick (see _reconcile). The same
reconciliation also drives the Observer-pattern event stream (see
state/game_events.py, state/snapshot_diff.py) that log/score panels subscribe
to, instead of each one independently diffing snapshots itself.
"""

from config import JUMP_TRAVEL_TIME, MOVE_TRAVEL_TIME_PER_CELL
from model.board import EMPTY

from state.game_events import GameOver, MoveAccepted, MoveRejected
from state.observer import Subject
from state.snapshot_diff import FrozenSnapshot, diff_completed_motion


def _chebyshev_distance(a, b) -> int:
    return max(abs(a.row - b.row), abs(a.col - b.col))


class PendingMotion:
    """A piece's predicted travel from source to destination.

    Timed with the exact same constants the server itself uses (imported, never
    re-derived), so in the common case our own "arrived" and the engine's
    "arrived" line up at the same tick instead of drifting apart. Also records
    what stood at the destination when the motion was requested, the same way
    the engine's own arrival logic does, so a completed motion can be told apart
    as a capture vs. a plain arrival without re-deriving it later.
    """

    def __init__(self, source, destination, token: str, duration_ms: float, is_jump: bool, expected_target: str):
        self.source = source
        self.destination = destination
        self.token = token
        self.duration_ms = duration_ms
        self.is_jump = is_jump
        self.expected_target = expected_target
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
            expected_target = snapshot.get_piece(destination)
            duration_ms = _chebyshev_distance(source, destination) * MOVE_TRAVEL_TIME_PER_CELL
            self._pending[source] = PendingMotion(
                source, destination, token, duration_ms, is_jump=False, expected_target=expected_target
            )
            self._events.publish(MoveAccepted(source, destination, token))
        else:
            self._events.publish(MoveRejected(source, destination, result.reason))
        return result

    def request_jump(self, source, destination) -> None:
        snapshot = self._engine.snapshot()
        token = snapshot.get_piece(source)
        expected_target = snapshot.get_piece(destination)
        self._engine.request_jump(source, destination)
        # request_jump has no return value to confirm acceptance; a jump silently
        # ignored by the engine (game over, already moving, out of bounds) is
        # caught the same way a stale move is - _reconcile() checks the real
        # snapshot once this predicted duration elapses, not before.
        if token != EMPTY:
            self._pending[source] = PendingMotion(
                source, destination, token, JUMP_TRAVEL_TIME, is_jump=True, expected_target=expected_target
            )

    def tick(self, dt_ms: int):
        """Advance the engine's real clock, then advance and reconcile predicted
        motions against it, publishing whatever events that reconciliation
        reveals. Returns the fresh snapshot."""
        prev_snapshot = FrozenSnapshot(self._engine.snapshot())
        game_over_before = self._engine.game_over
        self._engine.wait(dt_ms)
        curr_snapshot = self._engine.snapshot()

        for motion in self._pending.values():
            motion.advance(dt_ms)
        self._reconcile(prev_snapshot, curr_snapshot)

        if curr_snapshot.game_over and not game_over_before:
            self._events.publish(GameOver())
        return curr_snapshot

    def _reconcile(self, prev_snapshot, curr_snapshot) -> None:
        """Drop every motion whose predicted duration has elapsed, and publish
        the event(s) that explain what actually happened to it.

        By now the engine has already resolved it one way or another (arrival,
        capture, stale-target cancellation, or a mid-flight same-color halt) -
        engine.wait() in tick() always runs before this, so curr_snapshot is
        always ground truth for wherever the piece actually ended up.
        """
        completed = [source for source, motion in self._pending.items() if motion.is_due]
        for source in completed:
            motion = self._pending.pop(source)
            for event in diff_completed_motion(motion, prev_snapshot, curr_snapshot):
                self._events.publish(event)
