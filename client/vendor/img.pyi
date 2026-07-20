"""Type stub for the vendored img.py - read by pyright/Pylance only, never
executed. img.py itself stays untouched (course-provided, read-only - see
img.py's own docstring): every public method already guards `self.img is
None` at runtime before using it, so by the time any *caller* touches
`.img` (always via `Img().read(...)` or a SpriteSource.load_*() factory,
both of which guarantee a loaded image), it's genuinely non-optional -
this stub reflects that external contract instead of the internal
pre-`read()` transient state.
"""

import pathlib

import numpy as np

class Img:
    img: np.ndarray

    def __init__(self) -> None: ...
    def read(
        self,
        path: str | pathlib.Path,
        size: tuple[int, int] | None = None,
        keep_aspect: bool = False,
        interpolation: int = ...,
    ) -> Img: ...
    def draw_on(self, other_img: Img, x: int, y: int) -> None: ...
    def put_text(
        self,
        txt: str,
        x: int,
        y: int,
        font_size: float,
        color: tuple[int, int, int, int] = ...,
        thickness: int = 1,
    ) -> None: ...
    def show(self) -> None: ...
