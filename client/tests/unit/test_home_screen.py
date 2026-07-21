import cv2

from screens.home_screen import HomeScreen


def screen_for(on_play=lambda: None, on_rooms=lambda: None, width: int = 400, height: int = 300) -> HomeScreen:
    return HomeScreen("alice", 1200, on_play, on_rooms, width=width, height=height)


def _center_of(button) -> tuple[int, int]:
    return button.x + button.width // 2, button.y + button.height // 2


def test_clicking_the_play_button_calls_on_play():
    called = []
    screen = screen_for(on_play=lambda: called.append(True))
    x, y = _center_of(screen._play_button)
    screen.handle_mouse(cv2.EVENT_LBUTTONDOWN, x, y, 0, None)
    assert called == [True]


def test_clicking_the_rooms_button_calls_on_rooms():
    called = []
    screen = screen_for(on_rooms=lambda: called.append(True))
    x, y = _center_of(screen._rooms_button)
    screen.handle_mouse(cv2.EVENT_LBUTTONDOWN, x, y, 0, None)
    assert called == [True]


def test_clicking_outside_either_button_does_nothing():
    play_called, rooms_called = [], []
    screen = screen_for(on_play=lambda: play_called.append(True), on_rooms=lambda: rooms_called.append(True))
    screen.handle_mouse(cv2.EVENT_LBUTTONDOWN, 5, 5, 0, None)
    assert play_called == []
    assert rooms_called == []


def test_a_non_click_mouse_event_over_a_button_does_nothing():
    called = []
    screen = screen_for(on_play=lambda: called.append(True))
    screen.handle_mouse(cv2.EVENT_MOUSEMOVE, 200, 150, 0, None)
    assert called == []


def test_render_returns_a_canvas_sized_to_the_screen():
    screen = screen_for(width=400, height=300)
    canvas = screen.render()
    height, width = canvas.img.shape[:2]
    assert (width, height) == (400, 300)


def test_tick_does_not_raise():
    screen_for().tick(16)


def test_handle_key_does_not_raise():
    screen_for().handle_key(65)


def test_render_does_not_raise_with_a_status_message_set():
    screen = HomeScreen("alice", 1200, lambda: None, lambda: None, status="no opponent found, try again")
    screen.render()


def test_render_at_the_default_screen_size_does_not_raise():
    HomeScreen("alice", 1200, lambda: None, lambda: None).render()
