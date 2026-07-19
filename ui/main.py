import server_bridge  # noqa: F401  (must run before any server-rooted import below)

import ui_config
from animation.animation_clock import Clock
from chess_io.board_parser import BoardParser
from config import WS_HOST, WS_PORT
from engine.game_engine import GameEngine
from graphics.window import Window
from model.starting_position import STARTING_POSITION
from net import protocol
from network.network_game_facade import NetworkGameFacade
from network.ws_client import WsClient
from screens.game_screen import GameScreen
from screens.home_screen import HomeScreen
from screens.login_screen import LoginScreen
from screens.screen_manager import ScreenManager
from state.game_facade import GameFacade

_SERVER_URI = f"ws://{WS_HOST}:{WS_PORT}"


def build_local_game_screen() -> GameScreen:
    """Local hot-seat mode: two people sharing one board/mouse, wired to a
    real in-process GameEngine - no server needed. Not reachable from the
    home screen (Play always goes over the network now), but kept available
    for offline dev/testing without a running ws_server.py."""
    board = BoardParser().parse(STARTING_POSITION)
    return GameScreen(GameFacade(GameEngine(board)))


def main() -> None:
    window = Window(ui_config.WINDOW_TITLE)
    screen_manager = ScreenManager(window)
    clock = Clock()

    def build_home_screen(client, username: str, elo: int) -> HomeScreen:
        def on_play() -> None:
            # play requires having already logged in on this same connection
            # (see net/ws_server.py) - matchmaking then blocks this thread
            # until it finds a human within range or, failing that, a bot
            # (see net/matchmaking.py); there's no "searching..." UI state
            # yet, so this just waits.
            client.send(protocol.play())
            screen_manager.show(GameScreen(NetworkGameFacade(client)))

        return HomeScreen(username, elo, on_play)

    def build_login_screen() -> LoginScreen:
        client = WsClient(_SERVER_URI)

        def on_success(username: str, elo: int) -> None:
            screen_manager.show(build_home_screen(client, username, elo))

        return LoginScreen(client, on_success)

    screen_manager.show(build_login_screen())

    while window.poll():
        window.maintain_aspect_ratio()
        dt_ms = clock.tick()
        scene = screen_manager.render_frame(dt_ms)
        window.show_frame(scene)

    window.close()


if __name__ == "__main__":
    main()
