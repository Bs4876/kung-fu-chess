"""Adapts OpenCV's mouse-callback signature to server's Controller.click(x, y)."""

import cv2


class MouseController:
    """Forwards left-clicks on the game window into the real Controller."""

    def __init__(self, controller):
        self._controller = controller

    def handle_event(self, event, x, y, flags, param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            self._controller.click(x, y)
