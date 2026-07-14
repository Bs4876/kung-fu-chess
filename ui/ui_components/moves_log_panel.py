"""Subscribes to GameFacade's events and keeps a human-readable move history.

Deliberately does no snapshot-diffing of its own - see state/game_facade.py for
why that bookkeeping is centralized there instead of duplicated in every panel.
"""

from state.game_events import GameOver, MoveAccepted, PieceCaptured, Promotion

MAX_VISIBLE_LINES = 20


def _side_name(token: str) -> str:
    return "White" if token[0] == "w" else "Black"


def _cell_name(position) -> str:
    """Standard algebraic-style cell name (row 7 = rank 1, matching how the
    starting position places White's back rank at the bottom, row 0)."""
    return f"{chr(ord('a') + position.col)}{8 - position.row}"


class MovesLogPanel:
    """Appends one line per move/capture/promotion/game-over event, in order."""

    def __init__(self):
        self._lines: list[str] = []

    def handle_event(self, event) -> None:
        line = self._describe(event)
        if line is not None:
            self._lines.append(line)

    def lines(self) -> list[str]:
        """Most recent lines first, capped to what a sidebar can reasonably show."""
        return list(reversed(self._lines[-MAX_VISIBLE_LINES:]))

    def _describe(self, event) -> str | None:
        if isinstance(event, MoveAccepted):
            return f"{_side_name(event.token)} {event.token[1]} {_cell_name(event.source)}-{_cell_name(event.destination)}"
        if isinstance(event, PieceCaptured):
            if event.by_token is not None:
                return f"{_side_name(event.by_token)} {event.by_token[1]} captures {event.captured_token} at {_cell_name(event.position)}"
            return f"{event.captured_token} destroyed at {_cell_name(event.position)}"
        if isinstance(event, Promotion):
            return f"{_side_name(event.from_token)} promotes to {event.to_token[1]} at {_cell_name(event.position)}"
        if isinstance(event, GameOver):
            return "Game Over"
        return None  # MoveRejected, PieceArrived, PieceHalted: not log-worthy on their own
