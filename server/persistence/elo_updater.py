"""Bus subscriber that updates both players' ELO ratings once an
authenticated-vs-authenticated game ends - a concrete case of the event bus
decoupling rating updates from GameRoom's own engine-outcome loop: GameRoom
just publishes what happened, this reacts to it, neither knows about the
other beyond the GameEnded event shape.
"""

from net.game_room import GameEnded
from persistence.elo import update_ratings
from persistence.users_repository import User, UsersRepository


class EloUpdater:
    """Subscribe an instance of this to EventBus.subscribe_all - it ignores
    every event except GameEnded, and within that, every game except one
    where both colors were seated by a real (non-bot, authenticated) User."""

    def __init__(self, users: UsersRepository):
        self._users = users

    def __call__(self, topic_and_event: tuple) -> None:
        _, event = topic_and_event
        if not isinstance(event, GameEnded):
            return
        # GameEnded.white_player/black_player are deliberately opaque
        # (object | None - see game_room.py) since GameRoom itself never
        # needs to know they're Users; this is the one consumer that does.
        if not isinstance(event.white_player, User) or not isinstance(event.black_player, User):
            return  # anonymous and/or bot games don't affect ELO
        score_white = 1.0 if event.winner == "white" else 0.0 if event.winner == "black" else 0.5
        new_white, new_black = update_ratings(event.white_player.elo, event.black_player.elo, score_white)
        self._users.update_elo(event.white_player.username, new_white)
        self._users.update_elo(event.black_player.username, new_black)
