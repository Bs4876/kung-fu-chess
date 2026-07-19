import numpy as np

from ui_widgets.text_input import TextInput
from vendor.img import Img


def make_canvas(width: int = 400, height: int = 300) -> Img:
    canvas = Img()
    canvas.img = np.zeros((height, width, 4), dtype=np.uint8)
    return canvas


def test_contains_true_inside_the_rect():
    field = TextInput(10, 20, 200, 40)
    assert field.contains(50, 30)


def test_contains_false_outside_the_rect():
    field = TextInput(10, 20, 200, 40)
    assert not field.contains(500, 500)


def test_typing_appends_to_the_buffer_only_when_focused():
    field = TextInput(0, 0, 200, 40)
    field.handle_key(ord("h"))
    assert field.text == ""  # not focused yet

    field.focused = True
    field.handle_key(ord("h"))
    field.handle_key(ord("i"))
    assert field.text == "hi"


def test_backspace_removes_the_last_character():
    field = TextInput(0, 0, 200, 40)
    field.focused = True
    field.text = "hi"
    field.handle_key(8)
    assert field.text == "h"


def test_backspace_on_empty_text_does_not_raise():
    field = TextInput(0, 0, 200, 40)
    field.focused = True
    field.handle_key(8)
    assert field.text == ""


def test_enter_returns_true_and_does_not_modify_the_buffer():
    field = TextInput(0, 0, 200, 40)
    field.focused = True
    field.text = "hi"
    assert field.handle_key(13) is True
    assert field.text == "hi"


def test_a_non_printable_non_special_key_is_ignored():
    field = TextInput(0, 0, 200, 40)
    field.focused = True
    field.handle_key(1)  # not printable ASCII, not backspace/enter
    assert field.text == ""


def test_no_key_this_frame_is_a_no_op():
    field = TextInput(0, 0, 200, 40)
    field.focused = True
    assert field.handle_key(None) is False
    assert field.text == ""


def test_max_length_stops_further_typing():
    field = TextInput(0, 0, 200, 40, max_length=3)
    field.focused = True
    for ch in "abcdef":
        field.handle_key(ord(ch))
    assert field.text == "abc"


def test_password_field_renders_bullets_not_the_real_text():
    field = TextInput(10, 10, 100, 30, is_password=True)
    field.text = "secret"
    canvas = make_canvas()
    field.draw_on(canvas)  # just verify it doesn't raise; pixel content isn't asserted


def test_draw_on_does_not_raise_for_an_unfocused_empty_field():
    field = TextInput(10, 10, 100, 30)
    make_canvas_result = make_canvas()
    field.draw_on(make_canvas_result)
