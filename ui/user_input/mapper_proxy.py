"""Stable-identity indirection over a BoardMapper.

server's Controller and MouseController each store their mapper reference
permanently at construction. Zooming needs a fresh BoardMapper (a new
cell_size), but reconstructing Controller/MouseController on every zoom
keypress would lose in-progress click-selection state. Passing this proxy in
their place instead lets the mapper underneath be swapped out - Controller
and MouseController never need to know it happened.
"""


class MapperProxy:
    def __init__(self, mapper):
        self._mapper = mapper

    def replace(self, mapper) -> None:
        self._mapper = mapper

    def pixel_to_cell(self, x: int, y: int):
        return self._mapper.pixel_to_cell(x, y)
