"""Stage 0: prove the ui/ -> server/ wiring works. No graphics yet."""

import server_bridge  # noqa: F401  (must run before any server-rooted import below)

from chess_io.board_parser import BoardParser
from engine.game_engine import GameEngine
from model.position import Position
from model.starting_position import STARTING_POSITION


def build_engine() -> GameEngine:
    """Parse the standard opening position into a real, running GameEngine."""
    board = BoardParser().parse(STARTING_POSITION)
    return GameEngine(board)


def main() -> None:
    """Smoke test: the ui/server wiring and the opening position are both correct,
    before any graphics code exists."""
    engine = build_engine()
    print(engine.snapshot().get_piece(Position(0, 0)))  # expected: "bR"


if __name__ == "__main__":
    main()
