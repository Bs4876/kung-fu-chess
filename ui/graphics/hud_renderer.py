"""Composes the rendered board with a moves-log sidebar into one wider scene."""

_TEXT_COLOR = (255, 255, 255, 255)  # BGR(A) white
_TITLE_FONT_SIZE = 0.8
_LINE_FONT_SIZE = 0.55
_LINE_HEIGHT_PX = 26
_LEFT_PADDING_PX = 20
_TOP_PADDING_PX = 30


class HudRenderer:
    """Draws board_canvas onto a wider canvas with the moves log to its right."""

    def __init__(self, sprite_loader, sidebar_width: int):
        self._sprites = sprite_loader
        self._sidebar_width = sidebar_width

    def compose(self, board_canvas, moves_log_panel):
        """Return a new canvas: the board unchanged on the left, the moves log
        drawn in a sidebar on the right."""
        board_height, board_width = board_canvas.img.shape[:2]
        full_width = board_width + self._sidebar_width

        scene = self._sprites.load_panel_background(full_width, board_height)
        board_canvas.draw_on(scene, 0, 0)
        self._draw_moves_log(scene, moves_log_panel, sidebar_x=board_width)
        return scene

    def _draw_moves_log(self, scene, moves_log_panel, sidebar_x: int) -> None:
        x = sidebar_x + _LEFT_PADDING_PX
        y = _TOP_PADDING_PX
        scene.put_text("Moves", x, y, _TITLE_FONT_SIZE, color=_TEXT_COLOR)

        for line in moves_log_panel.lines():
            y += _LINE_HEIGHT_PX
            scene.put_text(line, x, y, _LINE_FONT_SIZE, color=_TEXT_COLOR)
