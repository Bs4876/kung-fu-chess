"""Graphical username entry, shown before the home screen.

The course spec allows login either "in a shell" or via a GUI; this is the
GUI option, styled like home_screen.py's dark-brown/cream wood palette so
it reads as the first screen of the same app rather than a bolted-on
dialog. Only types via cv2's own key capture (see graphics/window.py),
which only reliably reports printable ASCII - not a real IME - so typed
usernames are restricted to that range, same as a plain shell prompt would
effectively require anyway for this project's login (username only, no
password).

Purely a text box + Login button reporting what was typed - client/main.py
owns actually sending the login request and reacting to the result, the
same callback-based split home_screen.py's on_play/on_rooms already use.
"""

import cv2

import ui_config
from ui_components.sound_player import play_sound
from ui_widgets.button import Button
from ui_widgets.canvas import blank_canvas

_BACKSPACE_KEYS = (8, 127)
_ENTER_KEYS = (13, 10)
_PRINTABLE_RANGE = (32, 126)


def _centered_text(canvas, text: str, center_x: int, y: int, font_size: float, color: tuple, thickness: int = 1) -> None:
    (text_width, _text_height), _baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_size, thickness)
    canvas.put_text(text, center_x - text_width // 2, y, font_size, color=color, thickness=thickness)


class LoginScreen:
    def __init__(
        self, on_submit,
        width: int = ui_config.HOME_SCREEN_WIDTH, height: int = ui_config.HOME_SCREEN_HEIGHT,
        status: str = "",
    ):
        """on_submit(username) is called with the trimmed, non-empty
        username once Enter is pressed or the Login button is clicked -
        empty/whitespace-only input is silently ignored, same as the old
        shell prompt's reprompt-until-non-empty loop. status: an optional
        one-line message shown under the input (e.g. a connection error)."""
        self._on_submit = on_submit
        self._width = width
        self._height = height
        self._status = status
        self._username = ""
        self._cursor_elapsed_ms = 0
        self._cursor_visible = True

        self._title_y = height // 4
        self._divider_y = self._title_y + 30
        self._prompt_y = self._divider_y + 40

        input_width, input_height = ui_config.LOGIN_INPUT_WIDTH_PX, ui_config.LOGIN_INPUT_HEIGHT_PX
        self._input_x = (width - input_width) // 2
        self._input_y = self._prompt_y + 30
        self._input_bounds = (self._input_x, self._input_y, self._input_x + input_width, self._input_y + input_height)

        button_width, button_height = 160, 56
        self._login_button = Button(
            "Login",
            x=(width - button_width) // 2, y=self._input_y + input_height + 24,
            width=button_width, height=button_height,
        )
        self._status_y = self._login_button.y + button_height + 40

    def tick(self, dt_ms: int) -> None:
        self._cursor_elapsed_ms += dt_ms
        if self._cursor_elapsed_ms >= ui_config.LOGIN_CURSOR_BLINK_MS:
            self._cursor_elapsed_ms = 0
            self._cursor_visible = not self._cursor_visible

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
            canvas, "Enter a username to begin", center_x, self._prompt_y,
            ui_config.HOME_SCREEN_SUBTITLE_FONT_SIZE, ui_config.HOME_SCREEN_SUBTITLE_COLOR,
        )

        self._draw_input_box(canvas)
        self._login_button.draw_on(canvas)

        if self._status:
            _centered_text(canvas, self._status, center_x, self._status_y, 0.6, ui_config.HOME_SCREEN_STATUS_COLOR)
        return canvas

    def _draw_input_box(self, canvas) -> None:
        left, top, right, bottom = self._input_bounds
        border = 2
        canvas.img[top:bottom, left:right] = ui_config.HOME_SCREEN_PANEL_BORDER_COLOR
        canvas.img[top + border:bottom - border, left + border:right - border] = ui_config.HOME_SCREEN_PANEL_COLOR

        text = self._username + ("|" if self._cursor_visible else "")
        text_y = top + (bottom - top) // 2 + 8  # roughly centers the text's baseline vertically
        canvas.put_text(text, left + 14, text_y, ui_config.LOGIN_INPUT_FONT_SIZE, color=ui_config.HOME_SCREEN_TITLE_COLOR)

    def handle_mouse(self, event, x, y, flags, param) -> None:
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if self._login_button.contains(x, y):
            play_sound(ui_config.SOUND_CLICK)
            self._submit()

    def handle_key(self, key: int | None) -> None:
        if key is None:
            return
        if key in _ENTER_KEYS:
            self._submit()
        elif key in _BACKSPACE_KEYS:
            self._username = self._username[:-1]
        elif _PRINTABLE_RANGE[0] <= key <= _PRINTABLE_RANGE[1] and len(self._username) < ui_config.LOGIN_MAX_USERNAME_LENGTH:
            self._username += chr(key)

    def _submit(self) -> None:
        username = self._username.strip()
        if username:
            self._on_submit(username)
