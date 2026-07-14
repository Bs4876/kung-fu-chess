"""Turns a just-completed pending motion into the domain event(s) it represents.

A pure function, informed by the pending motion itself rather than a blind
two-board diff: board tokens alone can't distinguish an arrival from a capture
from a mid-flight halt without knowing what the motion actually intended.
"""

from model.board import EMPTY
from model.position import Position

from state.game_events import PieceArrived, PieceCaptured, PieceHalted, Promotion


class FrozenSnapshot:
    """An independent copy of a GameSnapshot's board tokens.

    GameSnapshot is a thin, live view over the engine's own mutable Board, not
    a true point-in-time copy - reading it again after engine.wait() shows the
    *new* state, not the old one. Diffing needs a real "before" to compare
    against, so this copies every token out into a plain dict up front.
    """

    def __init__(self, snapshot):
        self.rows = snapshot.rows
        self.cols = snapshot.cols
        self._tokens = {
            Position(row, col): snapshot.get_piece(Position(row, col))
            for row in range(snapshot.rows)
            for col in range(snapshot.cols)
        }

    def get_piece(self, pos: Position) -> str:
        return self._tokens[pos]


def diff_completed_motion(motion, prev_snapshot, curr_snapshot) -> list:
    """Given a motion that was pending and is now gone, work out - by comparing
    what the engine's snapshot shows now - which of the reconciliation cases
    actually happened."""
    if curr_snapshot.get_piece(motion.source) == motion.token:
        return []  # stale-target cancellation: it never left, nothing to report

    at_destination = curr_snapshot.get_piece(motion.destination)
    if at_destination != EMPTY and at_destination[0] == motion.token[0]:
        return _arrival_events(motion, at_destination)

    halted_at = _find_new_resting_cell(motion, prev_snapshot, curr_snapshot)
    if halted_at is not None:
        return [PieceHalted(source=motion.source, resting_at=halted_at, token=motion.token, is_jump=motion.is_jump)]

    return [PieceCaptured(position=motion.source, captured_token=motion.token, by_token=None, is_jump=motion.is_jump)]


def _arrival_events(motion, arrived_token: str) -> list:
    if arrived_token != motion.token:
        return [Promotion(position=motion.destination, from_token=motion.token, to_token=arrived_token, is_jump=motion.is_jump)]
    if motion.expected_target != EMPTY:
        return [PieceCaptured(
            position=motion.destination, captured_token=motion.expected_target, by_token=motion.token,
            is_jump=motion.is_jump,
        )]
    return [PieceArrived(source=motion.source, destination=motion.destination, token=motion.token, is_jump=motion.is_jump)]


def _find_new_resting_cell(motion, prev_snapshot, curr_snapshot) -> Position | None:
    """A mid-flight same-color halt leaves the piece resting somewhere that is
    neither its original source nor its intended destination. Find that cell by
    looking for the one place the token newly appears."""
    exclude = {motion.source, motion.destination}
    for row in range(curr_snapshot.rows):
        for col in range(curr_snapshot.cols):
            pos = Position(row, col)
            if pos in exclude:
                continue
            if curr_snapshot.get_piece(pos) == motion.token and prev_snapshot.get_piece(pos) != motion.token:
                return pos
    return None
