"""Stage 2: a real, non-blocking render loop with an FPS overlay and clean close."""

import server_bridge  # noqa: F401  (must run before any server-rooted import below)

import ui_config
from animation.animation_clock import Clock
from chess_io.board_parser import BoardParser
from config import CELL_SIZE
from engine.game_engine import GameEngine
from graphics.renderer import BoardRenderer
from graphics.sprite_loader import SpriteLoader
from graphics.window import Window
from model.starting_position import STARTING_POSITION


def build_engine() -> GameEngine:
    """Parse the standard opening position into a real, running GameEngine."""
    board = BoardParser().parse(STARTING_POSITION)
    return GameEngine(board)


def next_fps_reading(previous_fps: float, dt_ms: int) -> float:
    """Smooth the instantaneous per-frame FPS with an exponential moving average,
    so the overlay reads steadily instead of flickering every frame."""
    if dt_ms <= 0:
        return previous_fps
    instantaneous = 1000.0 / dt_ms
    if not previous_fps:
        return instantaneous
    return previous_fps * 0.9 + instantaneous * 0.1


def draw_fps_overlay(canvas, fps: float) -> None:
    canvas.put_text(f"FPS: {fps:.0f}", 10, 30, 1.0, color=(0, 255, 0, 255))


def main() -> None:
    engine = build_engine()
    sprite_loader = SpriteLoader(ui_config.ASSETS_DIR, ui_config.SKIN, CELL_SIZE)
    renderer = BoardRenderer(sprite_loader, CELL_SIZE)
    window = Window(ui_config.WINDOW_TITLE)
    clock = Clock()

    fps = 0.0
    while window.poll():
        dt_ms = clock.tick()
        engine.wait(dt_ms)
        fps = next_fps_reading(fps, dt_ms)

        canvas = renderer.render(engine.snapshot())
        draw_fps_overlay(canvas, fps)
        window.show_frame(canvas)

    window.close()


if __name__ == "__main__":
    main()
