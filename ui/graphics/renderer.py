"""Composes one frame: the board background plus every animated piece on it."""

from animation.piece_animator import PieceAnimator
from model.board import EMPTY
from model.position import Position


class BoardRenderer:
    """Draws a GameSnapshot onto a fresh canvas each call, animating each piece.

    A fresh board.png copy is loaded every frame (via sprite_loader) rather than
    reused, because Img.draw_on mutates pixels in place with no way to undo a draw.

    Keeps one PieceAnimator per occupied board cell, persisting across calls so
    each piece's animation timeline survives between frames.
    """

    def __init__(self, sprite_loader, cell_size: int):
        self._sprites = sprite_loader
        self._cell_size = cell_size
        self._animators: dict[Position, PieceAnimator] = {}

    def render(self, snapshot, dt_ms: int = 0, selected: Position | None = None):
        """Return a new Img with the board, every piece's current frame, and (if
        given) a highlight border around the selected cell, all drawn on it."""
        self._sync_animators(snapshot)
        self._advance_animators(dt_ms)

        canvas = self._sprites.load_board(snapshot.rows, snapshot.cols)
        self._draw_pieces(canvas)
        if selected is not None:
            self._draw_selection(canvas, selected)
        return canvas

    def _occupied_cells(self, snapshot) -> dict[Position, str]:
        occupied = {}
        for row in range(snapshot.rows):
            for col in range(snapshot.cols):
                pos = Position(row, col)
                token = snapshot.get_piece(pos)
                if token != EMPTY:
                    occupied[pos] = token
        return occupied

    def _sync_animators(self, snapshot) -> None:
        """Create an animator for each occupied cell (or replace it if the piece
        there changed, e.g. after a capture), and drop animators for empty cells."""
        occupied = self._occupied_cells(snapshot)

        for pos, token in occupied.items():
            existing = self._animators.get(pos)
            if existing is None or existing.token != token:
                self._animators[pos] = PieceAnimator(self._sprites, token)

        for pos in list(self._animators):
            if pos not in occupied:
                del self._animators[pos]

    def _advance_animators(self, dt_ms: int) -> None:
        for animator in self._animators.values():
            animator.tick(dt_ms)

    def _draw_pieces(self, canvas) -> None:
        for pos, animator in self._animators.items():
            sprite = animator.current_frame()
            sprite.draw_on(canvas, pos.col * self._cell_size, pos.row * self._cell_size)

    def _draw_selection(self, canvas, selected: Position) -> None:
        highlight = self._sprites.load_selection_highlight()
        highlight.draw_on(canvas, selected.col * self._cell_size, selected.row * self._cell_size)
