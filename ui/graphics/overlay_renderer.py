"""Owns the board's non-piece overlays - split out of BoardRenderer so it's
independently testable without cv2/Img (see protocols.SpriteSource).

Draw order (selection, then halt-flashes, then cooldown-fades, then the
game-over banner) is load-bearing, not cosmetic: Img.draw_on composites in
place onto a shared canvas, and a halted+cooling cell legitimately gets both
overlays stacked in this order.
"""

from model.position import Position


class OverlayRenderer:
    def __init__(self, sprite_source, cell_size: int):
        self._sprites = sprite_source
        self._cell_size = cell_size

    def draw(self, canvas, selected: Position | None, halted_positions: list | None,
             cooldown_fade_fractions: dict | None, game_over: bool) -> None:
        if selected is not None:
            self._draw_selection(canvas, selected)
        for pos in halted_positions or []:
            self._draw_halt_flash(canvas, pos)
        for pos, fraction in (cooldown_fade_fractions or {}).items():
            self._draw_cooldown_fade(canvas, pos, fraction)
        if game_over:
            self._draw_game_over_banner(canvas)

    def _draw_selection(self, canvas, selected: Position) -> None:
        highlight = self._sprites.load_selection_highlight()
        highlight.draw_on(canvas, selected.col * self._cell_size, selected.row * self._cell_size)

    def _draw_halt_flash(self, canvas, position: Position) -> None:
        flash = self._sprites.load_halt_flash()
        flash.draw_on(canvas, position.col * self._cell_size, position.row * self._cell_size)

    def _draw_cooldown_fade(self, canvas, position: Position, fraction: float) -> None:
        fade = self._sprites.load_cooldown_fade_frame(fraction)
        fade.draw_on(canvas, position.col * self._cell_size, position.row * self._cell_size)

    def _draw_game_over_banner(self, canvas) -> None:
        board_height = canvas.img.shape[0]
        canvas.put_text("GAME OVER", self._cell_size, board_height // 2, 1.6, color=(0, 0, 255, 255), thickness=3)
