# Kung-Fu Chess Client

A graphical client for the [`server/`](../server/README.md) game engine, built
entirely on the course-provided `Img` class (vendored in `client/vendor/img.py`) -
no PyGame/SFML/LWJGL anywhere. Always plays over a real WebSocket connection to
a running [`server/net/ws_server.py`](../server/net/README.md) - there is no
offline/local-only mode.

## Running it

Start the server first (from `server/`, in its own terminal):

```bash
python -m net.ws_server
```

Then, from `client/`:

```bash
python main.py
```

1. **Login is a real screen** (`screens/login_screen.py`) - the course spec
   allows either a shell prompt or a GUI for this, and this project uses the
   GUI: type a username into the on-screen box and press Enter (or click
   Login). There's no password - the same username always reuses the same
   account (created on first login) and its ELO rating.
2. The **home screen** opens with two buttons:
   - **Play** - automatic matchmaking within `MATCH_ELO_RANGE` (±100) of your
     ELO. Shows a "Searching for an opponent..." dialog (with Cancel) while
     it waits, instead of freezing the window; gives up after
     `MATCHMAKING_WAIT_MS` (60s) with no human found.
   - **Rooms** - a native dialog with a text box and Create/Join/Cancel
     buttons. **Create** generates a short, human-typeable room code (5
     characters, e.g. `7K4RN`) and shows it in a popup to share. **Join**
     enters the room whose code you type in - the second person to join
     becomes the Black player; anyone who joins after that (same code, same
     Join button) is seated as a **read-only viewer** who sees the game live.
3. In the game itself: click a piece, then click a destination square to move
   it. To jump instead (bypassing normal move legality), left-click to select
   a piece, then **right-click** the destination; clicking an already-selected
   piece's own square jumps it in place (a "dodge"). You can only ever select
   your own pieces - clicking an opponent's piece does nothing (capturing one
   as a move/jump destination still works normally). The window can be
   resized by dragging its edges (both dimensions scale together, so the
   board is never distorted). Esc or the window's close button quits.

## What it does

- Board and pieces rendered from `client/assets/` (course-provided sprites),
  animated per-piece (idle/move/jump/short_rest/long_rest) from each state's
  own `config.json`.
- Pieces glide smoothly between cells in real time instead of snapping on
  arrival - predicted client-side (`client/state/motion_tracker.py`) and
  reconciled against the server's actual outcome once it arrives. A predicted
  motion is kept pending for a short grace period past its own naive duration
  before being treated as abandoned, so an ordinary move's animation is never
  cut short by network/server-tick latency.
- Each side panel shows who you're actually playing against (`White - alice`
  / `Black - bob`, from the server's own seated usernames), a running score,
  and a two-column Time/Move table of that side's own move history.
- Score is the sum of the piece values of everything that side has captured
  (`PIECE_VALUES` in `server/model/piece_values.py`), not a raw capture count.
- A red flash marks a piece that halted mid-flight (same-color collision); a
  "GAME OVER" banner appears once a king is captured.
- A piece must rest after landing before it can be commanded again -
  `MOVE_COOLDOWN_MS` (5s) after a move, the shorter `JUMP_COOLDOWN_MS` (2s)
  after a jump (both in `server/config.py`). Trying to move it again too soon
  is silently rejected, same as any other illegal move. A fading yellow
  overlay on the cooling-down cell mirrors the same duration client-side
  (`client/ui_components/cooldown_tracker.py`).
- If your opponent disconnects mid-game, a countdown banner shows how long
  before they forfeit (`DISCONNECT_GRACE_MS`, 20s) - reconnecting within that
  window resumes the same game instead of forfeiting.
- Sound effects (move, capture, illegal move, promotion, game over) and a
  skin/name/sound-on-off preference are configurable in `client/settings.json`
  (`client/user_settings.py`) without touching code.

## Testing

Pure-logic pieces (animation state machine, motion interpolation, the
event/motion-tracking bookkeeping, the log/score panels, dialogs' widget
wiring) have real unit tests:

```bash
python -m pytest client/tests/unit -v
```

Rendering, animation feel, and click responsiveness aren't practically
automatable - run the app (two clients + one server) and actually play it. A
reasonable manual pass covers: Play matchmaking two clients together, Rooms
create/join, joining a third client into an already-running room as a
viewer, a plain move, a capture, a pawn promoting on the last row, two pieces
moving at once, a same-color collision (one halts before reaching the
other), trying to move a piece again immediately after it arrives (rejected
by cooldown) and again after cooldown elapses (should work), disconnecting
one client mid-game and reconnecting within the grace window, and capturing
a king (game over banner + no further moves accepted on either side).
