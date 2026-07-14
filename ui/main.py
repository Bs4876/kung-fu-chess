"""Stage 4: click-to-move via the real Controller, with the selected cell highlighted."""

import server_bridge  # noqa: F401  (must run before any server-rooted import below)

import ui_config
from animation.animation_clock import Clock
from chess_io.board_parser import BoardParser
from config import CELL_SIZE
from engine.game_engine import GameEngine
from graphics.renderer import BoardRenderer
from graphics.sprite_loader import SpriteLoader
from graphics.window import Window
from input.board_mapper import BoardMapper
from input.controller import Controller
from model.starting_position import STARTING_POSITION
from user_input.mouse_controller import MouseController


def build_engine() -> GameEngine:
    """Parse the standard opening position into a real, running GameEngine."""
    board = BoardParser().parse(STARTING_POSITION)
    return GameEngine(board)


def build_controller(engine: GameEngine) -> Controller:
    """Wire up server's own click-to-move Controller against this engine's board size."""
    snapshot = engine.snapshot()
    mapper = BoardMapper(snapshot.rows, snapshot.cols, CELL_SIZE)
    return Controller(engine, mapper)


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
    controller = build_controller(engine)
    sprite_loader = SpriteLoader(ui_config.ASSETS_DIR, ui_config.SKIN, CELL_SIZE)
    renderer = BoardRenderer(sprite_loader, CELL_SIZE)
    window = Window(ui_config.WINDOW_TITLE)
    window.set_mouse_callback(MouseController(controller).handle_event)
    clock = Clock()

    fps = 0.0
    while window.poll():
        dt_ms = clock.tick()
        engine.wait(dt_ms)
        fps = next_fps_reading(fps, dt_ms)

        # Controller doesn't expose selection via a public API; peeking at its
        # internal state is a pragmatic tradeoff to avoid duplicating it here.
        canvas = renderer.render(engine.snapshot(), dt_ms, selected=controller._selected)
        draw_fps_overlay(canvas, fps)
        window.show_frame(canvas)

    window.close()


if __name__ == "__main__":
    main()
