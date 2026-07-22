import cv2

import ui_config
from screens.login_screen import LoginScreen


def screen_for(on_submit=lambda username: None, width: int = 400, height: int = 300) -> LoginScreen:
    return LoginScreen(on_submit, width=width, height=height)


def _type(screen: LoginScreen, text: str) -> None:
    for ch in text:
        screen.handle_key(ord(ch))


def _center_of(button) -> tuple[int, int]:
    return button.x + button.width // 2, button.y + button.height // 2


def test_typing_then_enter_submits_the_trimmed_username():
    submitted = []
    screen = screen_for(on_submit=submitted.append)
    _type(screen, "  alice  ")
    screen.handle_key(13)
    assert submitted == ["alice"]


def test_typing_then_clicking_login_submits():
    submitted = []
    screen = screen_for(on_submit=submitted.append)
    _type(screen, "bob")
    x, y = _center_of(screen._login_button)
    screen.handle_mouse(cv2.EVENT_LBUTTONDOWN, x, y, 0, None)
    assert submitted == ["bob"]


def test_enter_with_no_username_typed_does_not_submit():
    submitted = []
    screen = screen_for(on_submit=submitted.append)
    screen.handle_key(13)
    assert submitted == []


def test_enter_with_only_whitespace_does_not_submit():
    submitted = []
    screen = screen_for(on_submit=submitted.append)
    _type(screen, "   ")
    screen.handle_key(13)
    assert submitted == []


def test_backspace_removes_the_last_character():
    submitted = []
    screen = screen_for(on_submit=submitted.append)
    _type(screen, "alicd")
    screen.handle_key(8)
    _type(screen, "e")
    screen.handle_key(13)
    assert submitted == ["alice"]


def test_username_is_capped_at_the_configured_max_length():
    submitted = []
    screen = screen_for(on_submit=submitted.append)
    _type(screen, "x" * (ui_config.LOGIN_MAX_USERNAME_LENGTH + 10))
    screen.handle_key(13)
    assert submitted == ["x" * ui_config.LOGIN_MAX_USERNAME_LENGTH]


def test_a_none_key_does_nothing():
    submitted = []
    screen = screen_for(on_submit=submitted.append)
    screen.handle_key(None)
    assert submitted == []


def test_clicking_outside_the_login_button_does_nothing():
    submitted = []
    screen = screen_for(on_submit=submitted.append)
    _type(screen, "alice")
    screen.handle_mouse(cv2.EVENT_LBUTTONDOWN, 5, 5, 0, None)
    assert submitted == []


def test_a_non_click_mouse_event_over_the_button_does_nothing():
    submitted = []
    screen = screen_for(on_submit=submitted.append)
    _type(screen, "alice")
    x, y = _center_of(screen._login_button)
    screen.handle_mouse(cv2.EVENT_MOUSEMOVE, x, y, 0, None)
    assert submitted == []


def test_render_returns_a_canvas_sized_to_the_screen():
    screen = screen_for(width=400, height=300)
    canvas = screen.render()
    height, width = canvas.img.shape[:2]
    assert (width, height) == (400, 300)


def test_tick_toggles_the_cursor_after_the_blink_interval():
    screen = screen_for()
    assert screen._cursor_visible is True
    screen.tick(ui_config.LOGIN_CURSOR_BLINK_MS)
    assert screen._cursor_visible is False


def test_render_does_not_raise_with_a_status_message_set():
    LoginScreen(lambda username: None, status="could not connect").render()


def test_render_at_the_default_screen_size_does_not_raise():
    LoginScreen(lambda username: None).render()
