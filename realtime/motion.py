from model.position import Position

MOVE_TRAVEL_TIME = 1000


class Motion:
    def __init__(self, piece_token: str, src: Position, dst: Position, start_time: int):
        self.piece_token = piece_token
        self.src = src
        self.dst = dst
        distance = max(abs(dst.row - src.row), abs(dst.col - src.col))
        self.arrival_time = start_time + distance * MOVE_TRAVEL_TIME


class ArrivalEvent:
    def __init__(self, piece_token: str, src: Position, dst: Position):
        self.piece_token = piece_token
        self.src = src
        self.dst = dst
