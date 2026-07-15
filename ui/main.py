import server_bridge  # noqa: F401  (must run before any server-rooted import below)

import ui_config
from animation.animation_clock import Clock
from chess_io.board_parser import BoardParser
from config import CELL_SIZE
from engine.game_engine import GameEngine
from graphics.hud_renderer import HudRenderer
from graphics.renderer import BoardRenderer
from graphics.sprite_loader import SpriteLoader
from graphics.window import Window
from input.board_mapper import BoardMapper
from input.controller import Controller
from model.starting_position import STARTING_POSITION
from state.game_facade import GameFacade
from ui_components.cooldown_tracker import CooldownTracker
from ui_components.game_over_banner import GameOverBanner
from ui_components.halt_flash import HaltFlashTracker
from ui_components.moves_log_panel import MovesLogPanel
from ui_components.player_labels import PlayerLabels
from ui_components.score_panel import ScorePanel
from user_input.mapper_proxy import MapperProxy
from user_input.mouse_controller import MouseController
from user_input.zoom_controller import ZoomController


def build_facade() -> GameFacade:
    """Parse the standard opening position into a real, running GameEngine,
    wrapped in a GameFacade so the UI can predict smooth in-flight motion."""
    board = BoardParser().parse(STARTING_POSITION)
    return GameFacade(GameEngine(board))


def build_mapper(facade: GameFacade) -> BoardMapper:
    snapshot = facade.snapshot()
    return BoardMapper(snapshot.rows, snapshot.cols, CELL_SIZE)


def build_controller(facade: GameFacade, mapper) -> Controller:
    """Wire up server's own click-to-move Controller against this facade.

    Controller only calls request_move(...)/snapshot() on whatever it's given,
    so pointing it at GameFacade instead of the raw engine needs no changes to
    Controller itself. mapper is a MapperProxy, not a raw BoardMapper - Controller
    only ever calls .pixel_to_cell(x, y) on it, so it can't tell the difference.
    """
    return Controller(facade, mapper)


def build_zoom_controller() -> ZoomController:
    return ZoomController(
        base_cell_size=CELL_SIZE,
        min_multiplier=ui_config.ZOOM_MIN_MULTIPLIER,
        max_multiplier=ui_config.ZOOM_MAX_MULTIPLIER,
        step=ui_config.ZOOM_STEP,
        zoom_in_keys=ui_config.ZOOM_KEYS_IN,
        zoom_out_keys=ui_config.ZOOM_KEYS_OUT,
    )


def build_render_stack(cell_size: int) -> tuple[SpriteLoader, BoardRenderer, HudRenderer]:
    """(Re)build the sprite loader and both renderers for one cell size.

    Every PieceAnimator caches frames pre-sized to whatever SpriteLoader built
    it, so a zoom-level change rebuilds this whole stack atomically rather
    than mutating cell_size in place - any in-flight animation restarts at
    frame 1 of its current state on the exact frame a zoom happens, a
    one-frame cosmetic blip rather than stale wrong-sized sprites everywhere.
    """
    sprite_loader = SpriteLoader(ui_config.ASSETS_DIR, ui_config.SKIN, cell_size)
    renderer = BoardRenderer(sprite_loader, cell_size)
    hud = HudRenderer(sprite_loader)
    return sprite_loader, renderer, hud


def main() -> None:
    facade = build_facade()
    start_snapshot = facade.snapshot()
    rows, cols = start_snapshot.rows, start_snapshot.cols

    mapper_proxy = MapperProxy(build_mapper(facade))
    controller = build_controller(facade, mapper_proxy)

    moves_log_panel = MovesLogPanel()
    facade.subscribe(moves_log_panel.handle_event)
    score_panel = ScorePanel()
    facade.subscribe(score_panel.handle_event)
    game_over_banner = GameOverBanner()
    facade.subscribe(game_over_banner.handle_event)
    halt_flash = HaltFlashTracker()
    facade.subscribe(halt_flash.handle_event)
    cooldown_tracker = CooldownTracker()
    facade.subscribe(cooldown_tracker.handle_event)
    player_labels = PlayerLabels()

    zoom = build_zoom_controller()
    sprite_loader, renderer, hud = build_render_stack(zoom.cell_size)
    window = Window(ui_config.WINDOW_TITLE)
    mouse_controller = MouseController(controller, facade, mapper_proxy, board_x_offset=ui_config.PANEL_WIDTH)
    window.set_mouse_callback(mouse_controller.handle_event)
    clock = Clock()

    while window.poll():
        zoomed = zoom.handle_key(window.consume_key())
        if zoomed:
            sprite_loader, renderer, hud = build_render_stack(zoom.cell_size)
            mapper_proxy.replace(BoardMapper(rows, cols, zoom.cell_size))

        dt_ms = clock.tick()
        # Age existing flashes/cooldowns by dt_ms *before* facade.tick() can
        # start new ones this frame - otherwise a cooldown that only just
        # started (from an arrival inside this very facade.tick() call) would
        # immediately get the same dt_ms credited to it a second time, aging
        # it past COOLDOWN_MS before it's ever drawn even once.
        halt_flash.tick(dt_ms)
        cooldown_tracker.tick(dt_ms)
        snapshot = facade.tick(dt_ms)

        # Controller doesn't expose selection via a public API; peeking at its
        # internal state is a pragmatic tradeoff to avoid duplicating it here.
        board_canvas = renderer.render(
            snapshot,
            dt_ms,
            selected=controller._selected,
            pending_motions=facade.pending_motions(),
            halted_positions=halt_flash.active_positions(),
            game_over=game_over_banner.is_game_over,
            cooldown_fade_fractions=cooldown_tracker.active_fade_frames(),
        )
        scene = hud.compose(board_canvas, moves_log_panel, score_panel, player_labels)
        if zoomed:
            window.resize_to(scene)
        window.show_frame(scene)

    window.close()


if __name__ == "__main__":
    main()
