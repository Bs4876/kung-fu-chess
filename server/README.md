# Kung-Fu Chess Server

Modular Python implementation of Kung-Fu Chess: a real-time chess variant where
pieces move along the board over simulated time instead of instantly, so
multiple moves can be in flight at once.

## Key Features
- **Clean Architecture:** High modularity with SRP and DRY principles.
- **Quality Assurance:** 100% unit test coverage.
- **Extensibility:** Built with Dependency Injection and a clean command router.

## Game Rules
- Pieces move at a fixed speed (`MOVE_TRAVEL_TIME_PER_CELL` ms per cell); the
  board only updates when a piece actually arrives, not when the move is issued.
- A pawn may advance two squares on its first move from its starting row.
- A pawn reaching the last row promotes to a queen.
- Capturing the opposing king ends the game.
- A piece can jump (`jump x y`) straight to a destination, bypassing normal
  move legality. Landing on an occupied square destroys whatever is there,
  even a piece of the same color.

## Extra Features
Beyond a single move at a time, this project also supports:
- **Concurrent motion:** different pieces may move at the same time; a piece
  already in motion rejects a second command for itself.
- **Mid-flight collision:** if two moving pieces' paths cross the same cell at
  the same simulated instant, the outcome depends on color: pieces of
  different colors collide and whichever started later wins, destroying the
  earlier piece and continuing on unaffected; pieces of the same color have
  the later one halt at the last safe cell before the meeting point instead
  of colliding.
- **Airborne interception:** while a piece is mid-jump, an enemy move that
  arrives on its destination square is destroyed instead of completing normally.
- **Stale-target cancellation:** a move is cancelled instead of completing if
  its destination's occupant changed since the move was accepted.
- **Cooldown after arrival:** a piece must rest for `COOLDOWN_MS` after landing
  (from a move or a jump) before it can be commanded again.

## Playing over a real network

`server/main.py`'s stdin/stdout CLI above is one entrypoint into the same
engine; `gateway/ws_server.py` is a second, independent one - a real
WebSocket server letting two separate client processes play each other, with:

- **Passwordless login** ("just for presentation") + **ELO rating**,
  persisted in SQLite (`persistence/`) and updated automatically when a game
  between two logged-in users ends.
- **Matchmaking** (`services/matchmaking_service.py`) - automatic pairing
  within an ELO range - and **manual rooms** (`services/room_service.py`) -
  create/join by a short human-typeable code, with anyone joining after the
  first two seated as a read-only viewer.
- **Disconnect/reconnect handling** - a dropped connection's seat is held for
  a grace period before forfeiting, and rejoining within that window resumes
  the same game.
- A durable, replayable **event log** of everything that happens, on both
  server and client (`persistence/event_log.py`).

### Shape of the networking layer

A small layered stack, each layer only calling the one directly beneath it:
`gateway/` (owns the real socket) -> `router/` (message_type -> handler) ->
`handlers/` (message -> service call + response) -> `services/` (business
logic, socket-agnostic).

- **`bus/event_bus.py`** - a topic-based publish/subscribe bus every other
  piece here publishes onto (game outcomes under `"game.<id>"`), so
  cross-cutting concerns (the write-log, ELO updates) can subscribe without
  the code that publishes needing to know they exist.
- **`protocol.py`** - the JSON wire envelope and every message shape, in one
  place. Swapping the encoding (e.g. to msgpack) later is a one-file change
  here, not a protocol redesign.
- **`gateway/ws_server.py`** (`Gateway`) - one instance per connection: the
  read loop, JSON decode, exception containment around dispatch, and cleanup
  on disconnect. The only module that touches `websockets` directly.
  **`gateway/connection.py`**/**`gateway/session.py`** hold that connection's
  mutable state (seated room, logged-in user).
- **`router/message_router.py`** - a table mapping each message type to its
  handler; replaces what used to be an if/elif chain in the connection
  handler itself.
- **`handlers/`** - one function per client message type
  (`auth_handler.py`, `matchmaking_handler.py`, `rooms_handler.py`,
  `gameplay_handler.py`), each thin: decode what the message means, call the
  right service, send the response.
- **`services/game_service.py`** (`GameRoom`) - owns one `GameEngine` and
  ticks it on its own asyncio task, independent of whether either player is
  currently connected. Also owns the disconnect grace-then-forfeit timer and
  reconnect handling for that game. **`services/game_registry.py`** tracks
  every active one by `game_id` so a rejoin can find its way back.
- **`services/matchmaking_service.py`** / **`services/room_service.py`** -
  the two ways a game actually gets created: automatic ELO-range pairing
  (giving up with an error if no human is found within a wait), or a
  manually created/joined room, identified by a short human-typeable code
  (e.g. `7K4RN`) rather than a raw uuid. Both terminate in an identical
  `GameRoom`, built from the same injected factory.
- **`persistence/`** - SQLite-backed accounts (username + ELO only, no
  password - "just for presentation", per the course spec: the same username
  always logs into the same account) and ELO rating updates, reacting to the
  bus rather than being called directly by `GameRoom`.

See [`../PROJECT_GUIDE.md`](../PROJECT_GUIDE.md) for a file-by-file map, and
[`../client/README.md`](../client/README.md) for the graphical client that
actually plays over this.

## Installation
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> If there is no `requirements.txt`, install `pytest` and `pytest-cov` manually:
>
> ```bash
> pip install pytest pytest-cov
> ```

## Usage
Run from this `server/` directory. The text-only CLI reads a board
definition + command script from standard input:

```bash
python main.py < input.txt
```

The real multiplayer server (see "Playing over a real network" above) is a
separate entrypoint and stays running until interrupted:

```bash
python -m gateway.ws_server
```

(Run it as a module, not `python gateway/ws_server.py` directly - the latter
puts `gateway/` itself on `sys.path` instead of `server/`, so `gateway/`'s own
sibling packages like `bus`/`persistence` fail to import.)

## Testing
Run the full unit test suite with coverage:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

## Notes
- Avoid using `monkeypatch` in unit tests; prefer dependency injection.
- Keep business rules configurable and avoid hard-coded game logic where possible.
- The code is designed to support future extension of custom piece movement rules.
