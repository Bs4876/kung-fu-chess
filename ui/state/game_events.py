"""Domain events GameFacade publishes for observers (moves log, score, ...)."""

from dataclasses import dataclass

from model.position import Position


@dataclass
class MoveAccepted:
    """A request_move/request_jump call was accepted - published synchronously,
    straight from the engine's own MoveResult, no diffing needed."""

    source: Position
    destination: Position
    token: str


@dataclass
class MoveRejected:
    source: Position
    destination: Position
    reason: str


@dataclass
class PieceArrived:
    """A piece completed its travel onto a previously-empty destination cell."""

    source: Position
    destination: Position
    token: str


@dataclass
class PieceCaptured:
    """An enemy piece is gone: either captured on arrival, or killed mid-flight
    (in which case by_token is unknown and left as None)."""

    position: Position
    captured_token: str
    by_token: str | None


@dataclass
class PieceHalted:
    """A piece stopped short of its intended destination - a mid-flight
    same-color collision - resting at some other cell instead."""

    source: Position
    resting_at: Position
    token: str


@dataclass
class Promotion:
    position: Position
    from_token: str
    to_token: str


@dataclass
class GameOver:
    pass
