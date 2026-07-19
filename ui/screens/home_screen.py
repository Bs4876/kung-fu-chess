"""The screen shown right after logging in: a welcome line naming who's
logged in, and one "Play" button - as trivial as this milestone's home
screen is meant to be. Clicking Play just reports the click; ui/main.py
owns actually sending the play command and switching to a GameScreen once
matchmaking finds an opponent (see build_network_game_screen in main.py).
"""

import cv2

import ui_config
from ui_widgets.button import Button
from ui_widgets.canvas import blank_canvas


class HomeScreen:
    def __init__(
        self, username: str, elo: int, on_play,
        width: int = ui_config.HOME_SCREEN_WIDTH, height: int = ui_config.HOME_SCREEN_HEIGHT,
    ):
        """on_play: called with no arguments when Play is clicked."""
        self._username = username
        self._elo = elo
        self._on_play = on_play
        self._width = width
        self._height = height
        button_width, button_height = 220, 70
        self._play_button = Button(
            "Play",
            x=(width - button_width) // 2,
            y=(height - button_height) // 2,
            width=button_width,
            height=button_height,
        )

    def tick(self, dt_ms: int) -> None:
        pass

    def render(self):
        canvas = blank_canvas(self._width, self._height, ui_config.HOME_SCREEN_BG_COLOR)
        canvas.put_text(
            "Kung Fu Chess",
            self._width // 2 - 170, self._height // 3 - 40,
            ui_config.HOME_SCREEN_TITLE_FONT_SIZE,
            color=ui_config.HOME_SCREEN_TITLE_COLOR, thickness=2,
        )
        canvas.put_text(
            f"Welcome, {self._username} (ELO {self._elo})",
            self._width // 2 - 140, self._height // 3,
            0.7, color=ui_config.HOME_SCREEN_TITLE_COLOR,
        )
        self._play_button.draw_on(canvas)
        return canvas

    def handle_mouse(self, event, x, y, flags, param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN and self._play_button.contains(x, y):
            self._on_play()

    def handle_key(self, key: int | None) -> None:
        pass
