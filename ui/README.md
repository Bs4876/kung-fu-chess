# Kung-Fu Chess UI

A graphical client for the [`server/`](../server/README.md) game engine, built
entirely on the course-provided `Img` class (vendored in `ui/vendor/img.py`) -
no PyGame/SFML/LWJGL anywhere.

## Running it

From the repository root:

```bash
uv run python ui/main.py
```

A window opens with the opening position. Click a piece, then click a
destination square to move it. To jump instead (bypassing normal move
legality), left-click to select a piece, then **right-click** the
destination. Esc or the window's close button quits.

## What it does

- Board and pieces rendered from `ui/assets/` (course-provided sprites),
  animated per-piece (idle/move/jump/short_rest/long_rest) from each state's
  own `config.json`.
- Pieces glide smoothly between cells in real time instead of snapping on
  arrival, predicted client-side and reconciled against the engine's actual
  outcome every frame (see `ui/state/game_facade.py`).
- Click-to-move via server's own `Controller`/`BoardMapper`, unmodified.
- A sidebar shows player names, a running score (captures per side), and a
  move-by-move log, all updated via an Observer/event stream published by
  `GameFacade` - see `ui/state/game_events.py`.
- A red flash marks a piece that halted mid-flight (same-color collision); a
  "GAME OVER" banner appears once a king is captured.
- A piece must rest after landing before it can be commanded again -
  `MOVE_COOLDOWN_MS` (3s) after a move, the shorter `JUMP_COOLDOWN_MS` (1.5s)
  after a jump (both in `server/config.py`). Trying to move it again too soon
  is rejected, same as any other illegal move, and shows up in the moves log
  with its reason ("cooldown"). A fading yellow overlay on the cooling-down
  cell mirrors the same duration client-side (`ui/ui_components/cooldown_tracker.py`).

## Testing

Pure-logic pieces (animation state machine, motion interpolation, the
snapshot-diffing that drives events, the log/score panels) have real unit
tests:

```bash
uv run python -m pytest ui/tests/unit -v
```

Rendering, animation feel, and click responsiveness aren't practically
automatable - run the app and actually play it. A reasonable manual pass
covers: a plain move, a capture, a pawn promoting on the last row, two pieces
moving at once, a same-color collision (one halts before reaching the other),
trying to move a piece again immediately after it arrives (should be rejected
by cooldown) and again after ~0.5s (should work), and capturing a king (game
over banner + no further moves accepted).
