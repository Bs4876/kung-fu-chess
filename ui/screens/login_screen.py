"""Username + password entry, backed by the server's login/register wire
messages (net/protocol.py's LOGIN/REGISTER/LOGIN_RESULT). Deliberately
minimal: two text fields, a Login button, a Register button - no "forgot
password", no client-side validation beyond what the server itself rejects.
"""

import cv2

import ui_config
from net import protocol
from ui_widgets.button import Button
from ui_widgets.canvas import blank_canvas
from ui_widgets.text_input import TextInput


class LoginScreen:
    def __init__(
        self, client, on_success,
        width: int = ui_config.LOGIN_SCREEN_WIDTH, height: int = ui_config.LOGIN_SCREEN_HEIGHT,
    ):
        """client: a connected ws_client-shaped object (send(message)/recv_all())
        - already open, not yet authenticated. on_success(username, elo) is
        called once the server confirms a successful login/register."""
        self._client = client
        self._on_success = on_success
        self._width = width
        self._height = height
        self._status = ""

        field_width, field_height = 280, 44
        field_x = (width - field_width) // 2
        self._username_field = TextInput(field_x, height // 2 - 70, field_width, field_height)
        self._password_field = TextInput(field_x, height // 2 - 10, field_width, field_height, is_password=True)
        self._username_field.focused = True

        button_width, button_height, gap = 130, 50, 20
        buttons_y = height // 2 + 60
        self._login_button = Button(
            "Login", x=width // 2 - button_width - gap // 2, y=buttons_y,
            width=button_width, height=button_height,
        )
        self._register_button = Button(
            "Register", x=width // 2 + gap // 2, y=buttons_y,
            width=button_width, height=button_height,
        )

    def tick(self, dt_ms: int) -> None:
        for message in self._client.recv_all():
            self._handle_message(message)

    def render(self):
        canvas = blank_canvas(self._width, self._height, ui_config.LOGIN_SCREEN_BG_COLOR)
        canvas.put_text(
            "Log in", self._width // 2 - 60, self._height // 2 - 110,
            ui_config.HOME_SCREEN_TITLE_FONT_SIZE, color=ui_config.LOGIN_SCREEN_TITLE_COLOR, thickness=2,
        )
        self._username_field.draw_on(canvas)
        self._password_field.draw_on(canvas)
        self._login_button.draw_on(canvas)
        self._register_button.draw_on(canvas)
        if self._status:
            canvas.put_text(
                self._status, self._username_field.x, self._password_field.y + self._password_field.height + 30,
                0.6, color=ui_config.LOGIN_SCREEN_STATUS_COLOR,
            )
        return canvas

    def handle_mouse(self, event, x, y, flags, param) -> None:
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if self._username_field.contains(x, y):
            self._focus(self._username_field)
        elif self._password_field.contains(x, y):
            self._focus(self._password_field)
        elif self._login_button.contains(x, y):
            self._submit(protocol.login)
        elif self._register_button.contains(x, y):
            self._submit(protocol.register)

    def handle_key(self, key: int | None) -> None:
        if self._username_field.handle_key(key):
            self._focus(self._password_field)
        elif self._password_field.handle_key(key):
            self._submit(protocol.login)

    def _handle_message(self, message: dict) -> None:
        if message["type"] != protocol.LOGIN_RESULT:
            return
        if message["success"]:
            self._on_success(message["username"], message["elo"])
        else:
            self._status = message["reason"] or "login failed"

    def _focus(self, field: TextInput) -> None:
        self._username_field.focused = False
        self._password_field.focused = False
        field.focused = True

    def _submit(self, message_builder) -> None:
        self._client.send(message_builder(self._username_field.text, self._password_field.text))
