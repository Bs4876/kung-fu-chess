"""A pixel-drawn single-line text field: a bordered box that appends/removes
characters from its own buffer in response to whichever key Window.last_key()
saw this frame, when it has focus. Password fields render their buffer as
bullets instead of the actual characters - the buffer itself is always the
real text either way.

The first keyboard-entry widget in the repo (every other widget so far only
needed mouse input) - key codes come from cv2.waitKey via Window.last_key(),
masked to a plain byte, so this only recognizes printable ASCII plus
backspace/enter rather than arrow keys, ctrl-combinations, etc.
"""

import ui_config
from vendor.img import Img

BACKSPACE = 8
ENTER_KEYS = (13, 10)


class TextInput:
    def __init__(self, x: int, y: int, width: int, height: int, is_password: bool = False, max_length: int = 32):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_password = is_password
        self.max_length = max_length
        self.text = ""
        self.focused = False

    def contains(self, x: int, y: int) -> bool:
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height

    def handle_key(self, key: int | None) -> bool:
        """Apply key to this field's buffer if focused. Returns True if
        Enter was pressed - the caller decides what that means (e.g. submit)."""
        if not self.focused or key is None:
            return False
        if key in ENTER_KEYS:
            return True
        if key == BACKSPACE:
            self.text = self.text[:-1]
        elif 32 <= key < 127 and len(self.text) < self.max_length:
            self.text += chr(key)
        return False

    def draw_on(self, canvas: Img) -> None:
        canvas.img[self.y:self.y + self.height, self.x:self.x + self.width] = ui_config.TEXT_INPUT_BG_COLOR
        border_color = (
            ui_config.TEXT_INPUT_FOCUSED_BORDER_COLOR if self.focused else ui_config.TEXT_INPUT_BORDER_COLOR
        )
        canvas.img[self.y, self.x:self.x + self.width] = border_color
        canvas.img[self.y + self.height - 1, self.x:self.x + self.width] = border_color
        canvas.img[self.y:self.y + self.height, self.x] = border_color
        canvas.img[self.y:self.y + self.height, self.x + self.width - 1] = border_color

        display_text = "*" * len(self.text) if self.is_password else self.text
        canvas.put_text(
            display_text, self.x + 10, self.y + self.height // 2 + 7,
            ui_config.TEXT_INPUT_FONT_SIZE, color=ui_config.TEXT_INPUT_TEXT_COLOR,
        )
