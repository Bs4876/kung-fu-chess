"""UI-only constants.

Deliberately not named `config.py` — `server/config.py` is also importable as bare
`config` once server_bridge runs, and reusing the name would risk a confusing
shadow-import bug.
"""

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

# Which sprite set to draw pieces with (ui/assets/<SKIN>/<CODE>/states/...).
SKIN = "pieces4"

WINDOW_TITLE = "Kung Fu Chess"

SIDEBAR_WIDTH = 320  # total sidebar width (kept for backward compat)
PANEL_WIDTH = 220    # width of each side panel (left=White, right=Black)

# main.py's FPS overlay.
FPS_OVERLAY_POSITION = (10, 30)
FPS_OVERLAY_COLOR = (0, 255, 0, 255)  # BGRA green
FPS_OVERLAY_FONT_SCALE = 1.0

# graphics/hud_renderer.py's sidebar layout.
HUD_TEXT_COLOR = (255, 255, 255, 255)  # BGRA white
HUD_SCORE_COLOR = (0, 255, 0, 255)  # BGRA green
HUD_TITLE_FONT_SIZE = 0.8
HUD_SCORE_FONT_SIZE = 0.65
HUD_LINE_FONT_SIZE = 0.55
HUD_LINE_HEIGHT_PX = 26
HUD_LEFT_PADDING_PX = 20
HUD_TOP_PADDING_PX = 30
HUD_SCORE_TO_MOVES_GAP_PX = 40

# ui_components/halt_flash.py
HALT_FLASH_DURATION_MS = 600

# ui_components/moves_log_panel.py
MOVES_LOG_MAX_VISIBLE_LINES = 20

# ui_components/cooldown_tracker.py - must match the number of pre-baked
# frames actually present in ui/assets/cooldown_fade/*.png.
COOLDOWN_FADE_FRAME_COUNT = 10

# graphics/window.py
WINDOW_ESC_KEY = 27

# user_input/zoom_controller.py - board zoom, keyboard-driven (not native OS
# window dragging - see graphics/window.py's docstring for why). Bounds chosen
# so every step lands on an integer pixel size at CELL_SIZE=100: 50/75/100/125/
# 150/175/200. '+'/'=' zoom in (same physical key, shifted or not); '-'/'_' out.
ZOOM_KEYS_IN = frozenset({ord("+"), ord("=")})
ZOOM_KEYS_OUT = frozenset({ord("-"), ord("_")})
ZOOM_MIN_MULTIPLIER = 0.5
ZOOM_MAX_MULTIPLIER = 2.0
ZOOM_STEP = 0.25
