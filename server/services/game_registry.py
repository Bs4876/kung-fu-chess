"""Tracks every currently-active GameRoom by game_id, so a dropped
connection's rejoin_game request can find its way back to the right room.
Also the single place new rooms get their game_id from.
"""

from bus.event_bus import EventBus
from chess_io.board_parser import BoardParser
from config import DISCONNECT_GRACE_MS
from model.starting_position import STARTING_POSITION
from services.game_service import GameRoom


class GameRegistry:
    def __init__(self, bus: EventBus, disconnect_grace_ms: int = DISCONNECT_GRACE_MS):
        self._bus = bus
        self._disconnect_grace_ms = disconnect_grace_ms
        self._rooms: dict[str, GameRoom] = {}
        self._next_id = 1

    def new_room(self) -> GameRoom:
        room = GameRoom(
            str(self._next_id), BoardParser().parse(STARTING_POSITION), self._bus,
            disconnect_grace_ms=self._disconnect_grace_ms,
        )
        self._next_id += 1
        room.start()
        self._rooms[room.game_id] = room
        return room

    def get(self, game_id: str) -> GameRoom | None:
        return self._rooms.get(game_id)
