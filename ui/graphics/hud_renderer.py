"""Composes the rendered board with a sidebar (score + moves log) into one scene."""

import ui_config


class HudRenderer:
    """Draws board_canvas onto a wider canvas with a score + moves-log sidebar."""

    def __init__(self, sprite_loader, sidebar_width: int):
        self._sprites = sprite_loader
        self._sidebar_width = sidebar_width

    def compose(self, board_canvas, moves_log_panel, score_panel, player_labels):
        """Return a new canvas: the board unchanged on the left, player names,
        score, and the moves log drawn in a sidebar on the right."""
        board_height, board_width = board_canvas.img.shape[:2]
        full_width = board_width + self._sidebar_width

        scene = self._sprites.load_panel_background(full_width, board_height)
        board_canvas.draw_on(scene, 0, 0)

        x = board_width + ui_config.HUD_LEFT_PADDING_PX
        y = self._draw_score(scene, score_panel, player_labels, x)
        self._draw_moves_log(scene, moves_log_panel, x, y + ui_config.HUD_SCORE_TO_MOVES_GAP_PX)
        return scene

    def _draw_score(self, scene, score_panel, player_labels, x: int) -> int:
        y = ui_config.HUD_TOP_PADDING_PX
        text = (
            f"{player_labels.white_name}: {score_panel.white_score}   "
            f"{player_labels.black_name}: {score_panel.black_score}"
        )
        scene.put_text(text, x, y, ui_config.HUD_SCORE_FONT_SIZE, color=ui_config.HUD_SCORE_COLOR)
        return y

    def _draw_moves_log(self, scene, moves_log_panel, x: int, start_y: int) -> None:
        y = start_y
        scene.put_text("Moves", x, y, ui_config.HUD_TITLE_FONT_SIZE, color=ui_config.HUD_TEXT_COLOR)

        for line in moves_log_panel.lines():
            y += ui_config.HUD_LINE_HEIGHT_PX
            scene.put_text(line, x, y, ui_config.HUD_LINE_FONT_SIZE, color=ui_config.HUD_TEXT_COLOR)
