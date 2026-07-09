from model.position import Position
from realtime.motion import Motion, ArrivalEvent


class RealTimeArbiter:
    def __init__(self):
        self._clock = 0
        self._motions: list[Motion] = []

    def has_active_motion(self) -> bool:
        return len(self._motions) > 0

    def start_motion(self, piece_token: str, src: Position, dst: Position) -> None:
        self._motions.append(Motion(piece_token, src, dst, self._clock))

    def advance_time(self, ms: int) -> list[ArrivalEvent]:
        self._clock += ms
        arrived = [m for m in self._motions if self._clock >= m.arrival_time]
        self._motions = [m for m in self._motions if self._clock < m.arrival_time]
        return [ArrivalEvent(m.piece_token, m.src, m.dst) for m in arrived]
