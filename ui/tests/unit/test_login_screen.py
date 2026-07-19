import cv2

from net import protocol
from screens.login_screen import LoginScreen


class FakeClient:
    def __init__(self):
        self.sent = []
        self._queue = []

    def send(self, message: dict) -> None:
        self.sent.append(message)

    def queue(self, message: dict) -> None:
        self._queue.append(message)

    def recv_all(self) -> list:
        messages, self._queue = self._queue, []
        return messages


def screen_for(width: int = 900, height: int = 700):
    client = FakeClient()
    successes = []
    screen = LoginScreen(client, on_success=lambda username, elo: successes.append((username, elo)), width=width, height=height)
    return screen, client, successes


def test_username_field_is_focused_by_default():
    screen, _client, _successes = screen_for()
    assert screen._username_field.focused
    assert not screen._password_field.focused


def test_clicking_the_password_field_focuses_it_and_unfocuses_username():
    screen, _client, _successes = screen_for()
    field = screen._password_field
    screen.handle_mouse(cv2.EVENT_LBUTTONDOWN, field.x + 5, field.y + 5, 0, None)
    assert field.focused
    assert not screen._username_field.focused


def test_typing_goes_to_whichever_field_is_focused():
    screen, _client, _successes = screen_for()
    for ch in "alice":
        screen.handle_key(ord(ch))
    assert screen._username_field.text == "alice"
    assert screen._password_field.text == ""


def test_enter_in_username_field_moves_focus_to_password():
    screen, _client, _successes = screen_for()
    screen.handle_key(13)
    assert screen._password_field.focused
    assert not screen._username_field.focused


def test_enter_in_password_field_submits_a_login_message():
    screen, client, _successes = screen_for()
    screen._username_field.text = "alice"
    screen._focus(screen._password_field)
    screen._password_field.text = "hunter2"

    screen.handle_key(13)

    assert client.sent == [protocol.login("alice", "hunter2")]


def test_clicking_login_sends_a_login_message_with_current_field_text():
    screen, client, _successes = screen_for()
    screen._username_field.text = "alice"
    screen._password_field.text = "hunter2"

    screen.handle_mouse(cv2.EVENT_LBUTTONDOWN,
                        screen._login_button.x + 5, screen._login_button.y + 5, 0, None)

    assert client.sent == [protocol.login("alice", "hunter2")]


def test_clicking_register_sends_a_register_message_with_current_field_text():
    screen, client, _successes = screen_for()
    screen._username_field.text = "alice"
    screen._password_field.text = "hunter2"

    screen.handle_mouse(cv2.EVENT_LBUTTONDOWN,
                        screen._register_button.x + 5, screen._register_button.y + 5, 0, None)

    assert client.sent == [protocol.register("alice", "hunter2")]


def test_successful_login_result_calls_on_success():
    screen, client, successes = screen_for()
    client.queue(protocol.login_result(True, None, "alice", 1200))
    screen.tick(0)
    assert successes == [("alice", 1200)]


def test_failed_login_result_sets_status_and_does_not_call_on_success():
    screen, client, successes = screen_for()
    client.queue(protocol.login_result(False, "invalid_credentials", None, None))
    screen.tick(0)
    assert successes == []
    assert screen._status == "invalid_credentials"


def test_non_login_messages_are_ignored():
    screen, client, successes = screen_for()
    client.queue({"type": "some_other_message"})
    screen.tick(0)
    assert successes == []


def test_render_returns_a_canvas_sized_to_the_screen():
    screen, _client, _successes = screen_for(width=900, height=700)
    canvas = screen.render()
    height, width = canvas.img.shape[:2]
    assert (width, height) == (900, 700)
