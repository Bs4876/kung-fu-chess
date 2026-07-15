"""Non-blocking window: Img.show() is a one-shot blocking call (imshow + waitKey(0)),
which can't drive a real-time game loop. This replaces it with per-frame polling,
mouse events, and close detection, using cv2 directly instead of Img.
"""

import cv2

from ui_config import WINDOW_ESC_KEY


class Window:
    """Owns one OpenCV window and its per-frame lifecycle.

    Fixed-size (cv2.WINDOW_AUTOSIZE), not resizable — this avoids having to
    translate resized-window screen coordinates back into native image pixel
    coordinates for mouse handling later.
    """

    def __init__(self, title: str):
        self._title = title
        self._last_key: int | None = None
        cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)

    def show_frame(self, canvas) -> None:
        """Display one rendered Img canvas as the current frame.

        A WINDOW_AUTOSIZE window automatically resizes itself to fit whatever
        image it's shown next - a differently-sized canvas (e.g. from a zoom
        level change) resizes the actual OS window with no extra call needed.
        """
        cv2.imshow(self._title, canvas.img)

    def poll(self) -> bool:
        """Pump this frame's window events. Returns False once the window should close
        (Esc pressed, or closed via the OS titlebar)."""
        raw_key = cv2.waitKey(1)
        # -1 means "no key this frame" - must check before masking with 0xFF,
        # since masking first would make that indistinguishable from keycode 255.
        self._last_key = None if raw_key == -1 else raw_key & 0xFF
        if self._last_key == WINDOW_ESC_KEY:
            return False
        return cv2.getWindowProperty(self._title, cv2.WND_PROP_VISIBLE) >= 1

    def consume_key(self) -> int | None:
        """Return this frame's key (if any) exactly once, then forget it."""
        key, self._last_key = self._last_key, None
        return key

    def set_mouse_callback(self, handler) -> None:
        """Register handler(event, x, y, flags, param) for mouse events on this window."""
        cv2.setMouseCallback(self._title, handler)

    def close(self) -> None:
        cv2.destroyWindow(self._title)
