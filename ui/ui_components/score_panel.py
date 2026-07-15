"""Subscribes to PieceCaptured events and tallies each side's capture count.

Score is fully derived here - the engine has no concept of scoring at all.
"""

from state.game_events import PieceCaptured


class ScorePanel:
    """score = number of enemy pieces a side has captured."""

    def __init__(self):
        self.white_score = 0
        self.black_score = 0

    def handle_event(self, event) -> None:
        # A mid-flight kill (by_token is None) has no identifiable capturer to
        # credit, so it's left out of both sides' tally rather than guessed at.
        if isinstance(event, PieceCaptured) and event.by_token is not None:
            self._credit(event.by_token[0])

    def _credit(self, capturing_color: str) -> None:
        if capturing_color == "w":
            self.white_score += 1
        else:
            self.black_score += 1

    def summary(self) -> str:
        return f"White: {self.white_score}   Black: {self.black_score}"
