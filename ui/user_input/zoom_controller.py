"""Tracks a discrete zoom level for the board, driven by keyboard input.

Deliberately not native OS window dragging (see graphics/window.py's docstring
for why: WINDOW_AUTOSIZE avoids having to translate resized-window screen
coordinates back into native image pixel coordinates for mouse handling).
Zoom is instead a multiplier on CELL_SIZE, changed a step at a time by
dedicated keys - the window itself then resizes automatically on the next
frame, since WINDOW_AUTOSIZE windows fit themselves to whatever image size
they're shown next.
"""


class ZoomController:
    """`.cell_size` is the current effective cell size in pixels."""

    def __init__(self, base_cell_size: int, min_multiplier: float, max_multiplier: float, step: float,
                 zoom_in_keys: frozenset[int], zoom_out_keys: frozenset[int]):
        self._base_cell_size = base_cell_size
        self._min_multiplier = min_multiplier
        self._max_multiplier = max_multiplier
        self._step = step
        self._zoom_in_keys = zoom_in_keys
        self._zoom_out_keys = zoom_out_keys
        self._multiplier = 1.0

    @property
    def cell_size(self) -> int:
        return round(self._base_cell_size * self._multiplier)

    def handle_key(self, key: int | None) -> bool:
        """Apply key if it's a zoom key. Returns whether the zoom level actually changed."""
        if key in self._zoom_in_keys:
            return self._set_multiplier(self._multiplier + self._step)
        if key in self._zoom_out_keys:
            return self._set_multiplier(self._multiplier - self._step)
        return False

    def _set_multiplier(self, new_multiplier: float) -> bool:
        clamped = min(max(new_multiplier, self._min_multiplier), self._max_multiplier)
        if clamped == self._multiplier:
            return False
        self._multiplier = clamped
        return True
