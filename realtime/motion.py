from model.position import Position
from config import MOVE_TRAVEL_TIME_PER_CELL


class Motion:
    def __init__(self, piece_token: str, src: Position, dst: Position, start_time: int):
        self.piece_token = piece_token
        self.src = src
        self.dst = dst
        distance = max(abs(dst.row - src.row), abs(dst.col - src.col))
        self.arrival_time = start_time + distance * MOVE_TRAVEL_TIME_PER_CELL


class ArrivalEvent:
    def __init__(self, piece_token: str, src: Position, dst: Position):
        self.piece_token = piece_token
        self.src = src
        self.dst = dst
