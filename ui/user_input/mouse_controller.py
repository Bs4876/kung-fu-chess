"""Adapts OpenCV's mouse-callback signature to server input.

Left-click reuses server's own Controller (select then move). Right-click
triggers a jump instead: it takes whatever piece is currently selected as the
source and jumps it to the clicked cell, bypassing normal move legality - the
Controller has no concept of jumps, so this talks to the facade directly.
"""

import cv2


class MouseController:
    def __init__(self, controller, facade, mapper):
        self._controller = controller
        self._facade = facade
        self._mapper = mapper

    def handle_event(self, event, x, y, flags, param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            self._controller.click(x, y)
        elif event == cv2.EVENT_RBUTTONDOWN:
            self._handle_jump(x, y)

    def _handle_jump(self, x, y) -> None:
        source = self._controller._selected
        if source is None:
            return
        destination = self._mapper.pixel_to_cell(x, y)
        if destination is not None:
            self._facade.request_jump(source, destination)
        self._controller._selected = None
