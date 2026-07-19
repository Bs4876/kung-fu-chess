from pathlib import Path

CELL_SIZE = 100
PIECE_SPEED = 100  # pixels per second
MOVE_TRAVEL_TIME_PER_CELL = 1000  # ms per cell
JUMP_TRAVEL_TIME = 1000  # ms
MOVE_COOLDOWN_MS = 5000  # ms a piece must rest after a normal move before it can act again
JUMP_COOLDOWN_MS = 2000  # ms a piece must rest after a jump before it can act again

GAME_LOG_DIR = Path(__file__).resolve().parent / "data" / "game_logs"  # durable per-game/system event log

SCHEMA_VERSION = 1  # bumped when a wire message's shape changes incompatibly
WS_HOST = "localhost"
WS_PORT = 8765
TICK_MS = 100  # how often each GameRoom advances its GameEngine's real-time clock

DB_PATH = Path(__file__).resolve().parent / "data" / "kungfuchess.db"
DEFAULT_ELO = 1200  # a commonly-recognized "average new player" anchor, not slide-mandated
ELO_K_FACTOR = 32  # standard default for lower-rated/provisional players, not slide-mandated
