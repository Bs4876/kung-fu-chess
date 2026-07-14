"""Build-time generator for the "pieces3" skin - not run by the game itself.

The course-provided skins (pieces1/pieces2) ship hand-drawn animation frames
per state. ui/assets/pieces3_source/ instead has one static image per piece
(no frame sequences), so each state's 5 frames here are generated
procedurally with simple affine transforms (scale/shear), anchored at the
bottom so a piece never appears to float off its square. Output matches
pieces1's exact folder/config convention
(ui/assets/<SKIN>/<CODE>/states/<STATE>/...), so SpriteLoader/PieceAnimator
need no changes to use it - only ui_config.SKIN has to point at "pieces3".

Re-run this after changing anything in ui/assets/pieces3_source/:

    uv run python ui/tools/generate_pieces3_skin.py
"""

import json
from pathlib import Path

import cv2
import numpy as np

_THIS_DIR = Path(__file__).resolve().parent
SRC_DIR = _THIS_DIR.parent / "assets" / "pieces3_source"
OUT_DIR = _THIS_DIR.parent / "assets" / "pieces3"

CODES = ["BB", "BW", "KB", "KW", "NB", "NW", "PB", "PW", "QB", "QW", "RB", "RW"]

# frames_per_sec/is_loop/next_state mirror pieces1's own values, so this skin
# feels consistent with the course-provided one it replaces.
STATE_TIMING = {
    "idle": dict(frames_per_sec=6, is_loop=True, next_state="idle"),
    "move": dict(frames_per_sec=12, is_loop=True, next_state="long_rest"),
    "jump": dict(frames_per_sec=8, is_loop=False, next_state="short_rest"),
    "short_rest": dict(frames_per_sec=8, is_loop=False, next_state="idle"),
    "long_rest": dict(frames_per_sec=6, is_loop=False, next_state="idle"),
}


def load_base(code: str):
    img = cv2.imread(str(SRC_DIR / f"{code}.png"), cv2.IMREAD_UNCHANGED)
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    return img


def scale_anchored_bottom(img, scale: float):
    """Scale vertically around the bottom edge: a "breathing" or
    squash/stretch effect that grows/shrinks a piece from the ground up,
    instead of making it appear to float."""
    h, w = img.shape[:2]
    new_h = max(1, round(h * scale))
    resized = cv2.resize(img, (w, new_h), interpolation=cv2.INTER_LINEAR)
    canvas = np.zeros((h, w, 4), dtype=np.uint8)
    if new_h <= h:
        canvas[h - new_h:h, :, :] = resized
    else:
        canvas[:, :, :] = resized[new_h - h:, :, :]
    return canvas


def shear_x(img, shear_amount: float):
    """Lean left/right: the bottom stays planted, the top shifts sideways."""
    h, w = img.shape[:2]
    matrix = np.float32([[1, -shear_amount, shear_amount * h], [0, 1, 0]])
    return cv2.warpAffine(img, matrix, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


def frames_for_idle(base):
    return [scale_anchored_bottom(base, s) for s in (1.00, 1.015, 1.03, 1.015, 1.00)]


def frames_for_move(base):
    return [shear_x(base, s) for s in (-0.04, -0.02, 0.0, 0.02, 0.04)]


def frames_for_jump(base):
    return [scale_anchored_bottom(base, s) for s in (1.0, 1.12, 1.18, 0.92, 1.0)]


def frames_for_short_rest(base):
    return [scale_anchored_bottom(base, s) for s in (0.94, 1.03, 0.99, 1.01, 1.0)]


def frames_for_long_rest(base):
    return [shear_x(base, s) for s in (0.03, -0.02, 0.01, -0.005, 0.0)]


FRAME_GENERATORS = {
    "idle": frames_for_idle,
    "move": frames_for_move,
    "jump": frames_for_jump,
    "short_rest": frames_for_short_rest,
    "long_rest": frames_for_long_rest,
}


def write_state(code_dir: Path, state: str, frames) -> None:
    state_dir = code_dir / "states" / state
    sprites_dir = state_dir / "sprites"
    sprites_dir.mkdir(parents=True, exist_ok=True)
    for i, frame in enumerate(frames, start=1):
        cv2.imwrite(str(sprites_dir / f"{i}.png"), frame)

    timing = STATE_TIMING[state]
    config = {
        "physics": {"speed_m_per_sec": 0.0, "next_state_when_finished": timing["next_state"]},
        "graphics": {"frames_per_sec": timing["frames_per_sec"], "is_loop": timing["is_loop"]},
    }
    (state_dir / "config.json").write_text(json.dumps(config, indent=2))


def main() -> None:
    for code in CODES:
        base = load_base(code)
        code_dir = OUT_DIR / code
        for state, generator in FRAME_GENERATORS.items():
            write_state(code_dir, state, generator(base))
        print(f"generated {code}")


if __name__ == "__main__":
    main()
