"""A trivial stand-in opponent: each tick, picks one random legal move from
its own pieces and requests it through the same GameRoom.handle_request_move
path a real player's move goes through (so its moves broadcast move_accepted
and animate for the human the same way theirs do) - not a real chess AI,
just enough to demonstrate the "no human found -> play vs bot" flow.
"""

import random

from model.board import EMPTY
from model.position import Position
from net import protocol


class BotPlayer:
    """Drives one color of a GameRoom, called once per tick by
    GameRoom._tick_loop (see GameRoom.attach_bot)."""

    def __init__(self, room, color: str, rng: random.Random = random):
        self._room = room
        self._color_prefix = "w" if color == "white" else "b"
        self._rng = rng

    def take_turn(self) -> None:
        """Try one random legal move this tick. A full no-op if none of its
        pieces currently have a legal destination (e.g. everything's
        mid-flight or on cooldown) - it just retries next tick, the same way
        a human player would simply not have moved yet."""
        candidates = self._candidate_moves()
        if not candidates:
            return
        source, destination = self._rng.choice(candidates)
        self._room.handle_request_move({
            "source": protocol.position_to_wire(source),
            "destination": protocol.position_to_wire(destination),
        })

    def _candidate_moves(self) -> list[tuple[Position, Position]]:
        snapshot = self._room.snapshot()
        board = snapshot.board
        moves = []
        for row in range(snapshot.rows):
            for col in range(snapshot.cols):
                source = Position(row, col)
                token = board.get_piece(source)
                if token == EMPTY or token[0] != self._color_prefix:
                    continue
                moves.extend((source, destination) for destination in self._room.legal_destinations(source))
        return moves
