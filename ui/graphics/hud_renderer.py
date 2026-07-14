"""Composes the rendered board with a sidebar (score + moves log) into one scene."""

_TEXT_COLOR = (255, 255, 255, 255)  # BGR(A) white
_SCORE_COLOR = (0, 255, 0, 255)  # BGR(A) green
_TITLE_FONT_SIZE = 0.8
_SCORE_FONT_SIZE = 0.65
_LINE_FONT_SIZE = 0.55
_LINE_HEIGHT_PX = 26
_LEFT_PADDING_PX = 20
_TOP_PADDING_PX = 30
_SCORE_TO_MOVES_GAP_PX = 40


class HudRenderer:
    """Draws board_canvas onto a wider canvas with a score + moves-log sidebar."""

    def __init__(self, sprite_loader, sidebar_width: int):
        self._sprites = sprite_loader
        self._sidebar_width = sidebar_width

    def compose(self, board_canvas, moves_log_panel, score_panel):
        """Return a new canvas: the board unchanged on the left, the score and
        moves log drawn in a sidebar on the right."""
        board_height, board_width = board_canvas.img.shape[:2]
        full_width = board_width + self._sidebar_width

        scene = self._sprites.load_panel_background(full_width, board_height)
        board_canvas.draw_on(scene, 0, 0)

        x = board_width + _LEFT_PADDING_PX
        y = self._draw_score(scene, score_panel, x)
        self._draw_moves_log(scene, moves_log_panel, x, y + _SCORE_TO_MOVES_GAP_PX)
        return scene

    def _draw_score(self, scene, score_panel, x: int) -> int:
        y = _TOP_PADDING_PX
        scene.put_text(score_panel.summary(), x, y, _SCORE_FONT_SIZE, color=_SCORE_COLOR)
        return y

    def _draw_moves_log(self, scene, moves_log_panel, x: int, start_y: int) -> None:
        y = start_y
        scene.put_text("Moves", x, y, _TITLE_FONT_SIZE, color=_TEXT_COLOR)

        for line in moves_log_panel.lines():
            y += _LINE_HEIGHT_PX
            scene.put_text(line, x, y, _LINE_FONT_SIZE, color=_TEXT_COLOR)
