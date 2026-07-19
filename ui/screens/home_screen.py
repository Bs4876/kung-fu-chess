"""The very first screen: a "Play" button plus a secondary "Login" button.

Deliberately still trivial. Play jumps straight into a networked game
exactly as before - it doesn't require login yet (that gating arrives once
real ELO matchmaking replaces the anonymous lobby it currently pairs
through). Login exists as its own reachable path so the login/register flow
can actually be used, without yet being a prerequisite for anything.
"""

import cv2

import ui_config
from ui_widgets.button import Button
from ui_widgets.canvas import blank_canvas


class HomeScreen:
    def __init__(
        self, on_play, on_login,
        width: int = ui_config.HOME_SCREEN_WIDTH, height: int = ui_config.HOME_SCREEN_HEIGHT,
    ):
        """on_play/on_login: called with no arguments when the matching button is clicked."""
        self._on_play = on_play
        self._on_login = on_login
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
        self._login_button = Button(
            "Login",
            x=(width - button_width) // 2,
            y=(height - button_height) // 2 + button_height + 20,
            width=button_width,
            height=button_height,
        )

    def tick(self, dt_ms: int) -> None:
        pass

    def render(self):
        canvas = blank_canvas(self._width, self._height, ui_config.HOME_SCREEN_BG_COLOR)
        canvas.put_text(
            "Kung Fu Chess",
            self._width // 2 - 170, self._height // 3,
            ui_config.HOME_SCREEN_TITLE_FONT_SIZE,
            color=ui_config.HOME_SCREEN_TITLE_COLOR, thickness=2,
        )
        self._play_button.draw_on(canvas)
        self._login_button.draw_on(canvas)
        return canvas

    def handle_mouse(self, event, x, y, flags, param) -> None:
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if self._play_button.contains(x, y):
            self._on_play()
        elif self._login_button.contains(x, y):
            self._on_login()

    def handle_key(self, key: int | None) -> None:
        pass
