"""Running `pytest` from the repo root needs both server/ and ui/ on sys.path -
each suite's bare imports (server's `from model.board import Board`, ui's
`import ui_config`) only resolve today because each is normally run with its
own directory as cwd (`cd server && pytest`, ui/tests/conftest.py for the
other direction). This does the same thing for a root-level collection run.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent

for _subdir in ("server", "ui"):
    _path = str(_ROOT / _subdir)
    if _path not in sys.path:
        sys.path.insert(0, _path)
