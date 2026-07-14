"""Non-blocking window: Img.show() is a one-shot blocking call (imshow + waitKey(0)),
which can't drive a real-time game loop. This replaces it with per-frame polling,
mouse events, and close detection, using cv2 directly instead of Img.
"""

import cv2

_ESC_KEY = 27


class Window:
    """Owns one OpenCV window and its per-frame lifecycle.

    Fixed-size (cv2.WINDOW_AUTOSIZE), not resizable — this avoids having to
    translate resized-window screen coordinates back into native image pixel
    coordinates for mouse handling later.
    """

    def __init__(self, title: str):
        self._title = title
        cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)

    def show_frame(self, canvas) -> None:
        """Display one rendered Img canvas as the current frame."""
        cv2.imshow(self._title, canvas.img)

    def poll(self) -> bool:
        """Pump this frame's window events. Returns False once the window should close
        (Esc pressed, or closed via the OS titlebar)."""
        key = cv2.waitKey(1) & 0xFF
        if key == _ESC_KEY:
            return False
        return cv2.getWindowProperty(self._title, cv2.WND_PROP_VISIBLE) >= 1

    def set_mouse_callback(self, handler) -> None:
        """Register handler(event, x, y, flags, param) for mouse events on this window."""
        cv2.setMouseCallback(self._title, handler)

    def close(self) -> None:
        cv2.destroyWindow(self._title)
