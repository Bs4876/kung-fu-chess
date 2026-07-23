"""The screen shown right after logging in: a welcome line naming who's
logged in, a "Play" button, and a "Rooms" button - as trivial as this
milestone's home screen is meant to be. Clicking either just reports the
click; client/main.py owns actually sending the play/rooms commands and
switching screens once a game is found (see build_home_screen in main.py).

Pure flat shapes and text (no imagery) in the same dark-brown/cream wood
palette as the board itself and the in-game HUD panels, so this screen
reads as part of the same game rather than a generic launcher.
"""

import cv2

import ui_config
from ui_components.sound_player import play_sound
from ui_widgets.button import Button
from ui_widgets.canvas import blank_canvas


def _centered_text(canvas, text: str, center_x: int, y: int, font_size: float, color: tuple, thickness: int = 1) -> None:
    (text_width, _text_height), _baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_size, thickness)
    canvas.put_text(text, center_x - text_width // 2, y, font_size, color=color, thickness=thickness)


class HomeScreen:
    def __init__(
        self, username: str, elo: int, on_play, on_rooms,
        width: int = ui_config.HOME_SCREEN_WIDTH, height: int = ui_config.HOME_SCREEN_HEIGHT,
        status: str = "",
    ):
        """on_play/on_rooms: called with no arguments when the matching
        button is clicked. status: an optional one-line message shown below
        the buttons (e.g. "no opponent found, try again" after a failed
        matchmaking attempt) - the same status-line pattern the now-removed
        LoginScreen/RoomsScreen used to use.

        Every y-coordinate below is laid out top-down and derived from the
        one before it (never independently re-derived at render time), so
        the title/divider/subtitle/panel/status blocks can never visually
        collide regardless of screen height.
        """
        self._username = username
        self._elo = elo
        self._on_play = on_play
        self._on_rooms = on_rooms
        self._width = width
        self._height = height
        self._status = status

        self._title_y = height // 4
        self._divider_y = self._title_y + 30
        self._subtitle_y = self._divider_y + 40

        button_width, button_height = 220, 70
        panel_pad_x, panel_pad_y = 50, 30
        button_x = (width - button_width) // 2
        panel_top = self._subtitle_y + 40  # clear gap below the subtitle's own text

        self._play_button = Button("Play", x=button_x, y=panel_top + panel_pad_y, width=button_width, height=button_height)
        self._rooms_button = Button(
            "Rooms", x=button_x, y=self._play_button.y + button_height + 20, width=button_width, height=button_height,
        )
        panel_bottom = self._rooms_button.y + button_height + panel_pad_y
        self._panel_bounds = (button_x - panel_pad_x, panel_top, button_x + button_width + panel_pad_x, panel_bottom)
        self._status_y = panel_bottom + 40

    def tick(self, dt_ms: int) -> None:
        pass

    def render(self):
        canvas = blank_canvas(self._width, self._height, ui_config.HOME_SCREEN_BG_COLOR)
        center_x = self._width // 2

        _centered_text(
            canvas, "Kung Fu Chess", center_x, self._title_y,
            ui_config.HOME_SCREEN_TITLE_FONT_SIZE, ui_config.HOME_SCREEN_TITLE_COLOR, thickness=2,
        )
        divider_half_width = 160
        canvas.img[self._divider_y:self._divider_y + 2, center_x - divider_half_width:center_x + divider_half_width] = (
            ui_config.HOME_SCREEN_DIVIDER_COLOR
        )
        _centered_text(
            canvas, f"Welcome, {self._username} (ELO {self._elo})", center_x, self._subtitle_y,
            ui_config.HOME_SCREEN_SUBTITLE_FONT_SIZE, ui_config.HOME_SCREEN_SUBTITLE_COLOR,
        )

        self._draw_button_panel(canvas)
        self._play_button.draw_on(canvas)
        self._rooms_button.draw_on(canvas)

        if self._status:
            _centered_text(canvas, self._status, center_x, self._status_y, 0.6, ui_config.HOME_SCREEN_STATUS_COLOR)
        return canvas

    def _draw_button_panel(self, canvas) -> None:
        """A bordered card behind the buttons - gives the screen some
        structure now that there's no imagery to anchor it, in the same
        panel/divider language graphics/hud_renderer.py already uses
        in-game."""
        left, top, right, bottom = self._panel_bounds
        border = 3
        canvas.img[top:bottom, left:right] = ui_config.HOME_SCREEN_PANEL_BORDER_COLOR
        canvas.img[top + border:bottom - border, left + border:right - border] = ui_config.HOME_SCREEN_PANEL_COLOR

    def handle_mouse(self, event, x, y, flags, param) -> None:
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if self._play_button.contains(x, y):
            play_sound(ui_config.SOUND_CLICK)
            self._on_play()
        elif self._rooms_button.contains(x, y):
            play_sound(ui_config.SOUND_CLICK)
            self._on_rooms()

    def handle_key(self, key: int | None) -> None:
        pass
