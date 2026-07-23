from bus.event_bus import EventBus
from services.game_registry import GameRegistry


async def test_new_room_is_findable_by_its_own_game_id():
    games = GameRegistry(EventBus())
    room = games.new_room()
    assert games.get(room.game_id) is room
    room.stop()


async def test_each_new_room_gets_a_distinct_game_id():
    games = GameRegistry(EventBus())
    first = games.new_room()
    second = games.new_room()
    assert first.game_id != second.game_id
    first.stop()
    second.stop()


def test_get_with_an_unknown_game_id_returns_none():
    games = GameRegistry(EventBus())
    assert games.get("no-such-game") is None
