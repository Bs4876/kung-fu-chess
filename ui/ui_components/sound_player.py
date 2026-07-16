"""Plays a short sound effect for each event GameFacade publishes.

winsound.PlaySound(..., SND_ASYNC) fires the clip on a background thread and
returns immediately, so this never blocks the render loop; SND_FILENAME|
SND_ASYNC together also mean a new call interrupts whatever this same process
was already playing, which is fine here since these are all short one-shots.
"""

import winsound

import ui_config
from state.game_events import GameOver, MoveAccepted, MoveRejected, PieceCaptured, Promotion

_SOUND_FOR_EVENT = {
    MoveAccepted: ui_config.SOUND_MOVE,
    MoveRejected: ui_config.SOUND_ILLEGAL_MOVE,
    PieceCaptured: ui_config.SOUND_CAPTURE,
    Promotion: ui_config.SOUND_PROMOTION,
    GameOver: ui_config.SOUND_GAME_OVER,
}


class SoundPlayer:
    """Subscribe this to GameFacade's moves/outcomes/game_over channels - it
    only reacts to the event types in _SOUND_FOR_EVENT, ignoring the rest."""

    def handle_event(self, event) -> None:
        path = _SOUND_FOR_EVENT.get(type(event))
        if path is not None:
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
