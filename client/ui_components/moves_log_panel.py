"""Subscribes to GameFacade's events and keeps a human-readable move history.

Deliberately does no snapshot-diffing of its own - see state/game_facade.py for
why that bookkeeping is centralized there instead of duplicated in every panel.
"""

from ui_config import BOARD_ROWS, MOVES_LOG_MAX_VISIBLE_LINES

from state.game_events import MoveAccepted


def _cell_name(position) -> str:
    """Standard algebraic-style cell name (row 7 = rank 1, matching how the
    starting position places White's back rank at the bottom, row 0)."""
    return f"{chr(ord('a') + position.col)}{BOARD_ROWS - position.row}"


def _format_time(ms: int) -> str:
    total_sec = ms / 1000.0
    return f"{total_sec:.1f}s"


class MovesLogPanel:
    """Keeps two separate move histories: one per side, each a list of
    (time, move) rows for a two-column table display."""

    def __init__(self):
        self._white_rows: list[tuple[str, str]] = []
        self._black_rows: list[tuple[str, str]] = []

    def handle_event(self, event) -> None:
        if isinstance(event, MoveAccepted):
            row = (
                _format_time(event.timestamp_ms),
                f"{event.token[1]} {_cell_name(event.source)}-{_cell_name(event.destination)}",
            )
            if event.token[0] == "w":
                self._white_rows.append(row)
            else:
                self._black_rows.append(row)

    def white_lines(self) -> list[tuple[str, str]]:
        return list(reversed(self._white_rows[-MOVES_LOG_MAX_VISIBLE_LINES:]))

    def black_lines(self) -> list[tuple[str, str]]:
        return list(reversed(self._black_rows[-MOVES_LOG_MAX_VISIBLE_LINES:]))
