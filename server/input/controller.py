from input.board_mapper import BoardMapper
from model.board import EMPTY


class Controller:
    def __init__(self, engine, board_mapper: BoardMapper):
        self._engine = engine
        self._mapper = board_mapper
        self._selected = None

    @property
    def selected(self):
        """The currently selected cell, or None - read-only: callers outside
        click()'s own select/move/deselect flow should use deselect(), not
        assign this directly."""
        return self._selected

    def deselect(self) -> None:
        """Clear the current selection without issuing a move - for input
        paths outside click()'s own select-then-move flow (e.g. a caller
        implementing jump-in-place or a right-click jump)."""
        self._selected = None

    def click(self, x: int, y: int) -> None:
        pos = self._mapper.pixel_to_cell(x, y)

        if pos is None:
            self._selected = None
            return

        snap = self._engine.snapshot()

        if self._selected is None:
            if snap.get_piece(pos) != EMPTY:
                self._selected = pos
        else:
            selected_token = snap.get_piece(self._selected)
            token_at_pos = snap.get_piece(pos)
            if token_at_pos != EMPTY and selected_token != EMPTY and token_at_pos[0] == selected_token[0]:
                self._selected = pos
            else:
                self._engine.request_move(self._selected, pos)
                self._selected = None
