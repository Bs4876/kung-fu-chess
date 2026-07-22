# Kung Fu Chess — Project Guide

A personal map of the codebase: what's in every file, and which design patterns tie it
together. Written for learning the project, not part of the graded deliverable itself —
delete or ignore it if you don't want it in the submission.

## The big picture

Real-time chess variant: moves take real time to travel across the board instead of being
instant, so multiple moves can be mid-flight from both sides at once, and same-color pieces
can collide mid-flight. The repo is two independent halves:

- **`server/`** — the game engine, rules, and (later) a WebSocket server. No UI code at all.
- **`client/`** — the graphical client (renamed from `ui/` on 2026-07-20). Built entirely on
  a vendored `Img` class (no PyGame/SFML). Talks to `server/` two ways: importing its pure
  Python modules directly via a `sys.path` trick (`client/server_bridge.py`) for shared
  domain logic (`model`, `rules`, `config`), and talking to a *running* server process over a
  real WebSocket for actual multiplayer.

Recommended reading order (simple → complex, roughly how it was built):
`model/` → `rules/` → `engine/game_engine.py` + `realtime/` → `engine/observer.py` →
`net/` (the server) → `client/main.py` → `client/network/` → `client/screens/`.

---

## `server/`

### `model/` — pure data, no behavior beyond basic queries
| File | What it is |
|---|---|
| `position.py` | `Position(row, col)` — a board cell. Hashable/equatable, used as dict keys everywhere (pending motions, cooldowns). |
| `board.py` | `Board` — a 2D grid of piece tokens (`"."` = empty). Bounds checking, get/move/replace piece. No rules knowledge. |
| `piece.py` | Piece token parsing/symbols (`_KIND_MAP` etc.) — the single-letter+color encoding (`"KW"`, `"PB"`, ...) used everywhere. |
| `piece_values.py` | Standard chess material values per piece kind, keyed by symbol — used by the client's score panel. |
| `game_state.py` | `GameState` — thin `(board, game_over)` read-only pair. |
| `starting_position.py` | The standard opening position as text, in `BoardParser`'s format. |

### `chess_io/` — text format in/out (used by the CLI, `server/main.py`)
| File | What it is |
|---|---|
| `board_parser.py` | Text → `Board`. |
| `board_printer.py` | `Board`/snapshot → text (for the CLI's `print board` command). |

### `rules/` — legal-move logic, no timing
| File | What it is |
|---|---|
| `piece_rules.py` | Per-piece-kind legal-destination logic (sliding pieces, knight jumps, pawn rules, etc.) — pure functions over a `Board`. |
| `rule_engine.py` | `RuleEngine` — validates a single move request (`validate_move`) and lists `legal_destinations` for a piece, built on `piece_rules.py`. |

### `realtime/` — the "moves take time" machinery
| File | What it is |
|---|---|
| `motion.py` | `Motion` — one piece's travel from src to dst with a start/arrival time; `ArrivalEvent`/`CollisionEvent`; `straight_line_meeting_time` (the math for when two motions cross paths). |
| `real_time_arbiter.py` | `RealTimeArbiter` — owns every in-flight `Motion` plus cooldowns, and figures out (given the current clock) who has arrived and who has collided with whom. |

### `engine/` — the orchestrator
| File | What it is |
|---|---|
| `game_engine.py` | `GameEngine` — the single source of truth. Accepts move/jump requests, validates via `RuleEngine`, hands motion to `RealTimeArbiter`, and on `wait(dt_ms)` resolves whatever the arbiter says happened into `Arrived`/`Captured`/`Halted`/`Promoted` outcome objects — publishing each one the instant it resolves. Also exposes `GameSnapshot`, a read-only view for callers. |
| `observer.py` | `Subject` — a generic pub/sub primitive, no game knowledge. (Deliberately duplicated in `client/state/observer.py` rather than shared, so `server/` stays dependency-free of `client/`.) |

### `input/` — click-to-move, shared between the CLI and (via the client's `MouseController`) the GUI
| File | What it is |
|---|---|
| `board_mapper.py` | `BoardMapper` — pixel ↔ board-cell coordinate conversion. |
| `controller.py` | `Controller` — click-then-click-again select/move flow on top of an engine-shaped object. |

### `net/` — the WebSocket server (the newest, most complex part)
| File | What it is |
|---|---|
| `protocol.py` | Every wire message shape as plain-dict builder functions + `encode`/`decode` (JSON) + dict↔engine-dataclass translation. The one place that knows about the wire format. |
| `session.py` | `Session` — per-connection state: which logged-in user (if any) owns this socket. |
| `auth.py` | `handle_login` — fetch-or-create a user by username (no password — "just for presentation" per the course spec). |
| `game_room.py` | `GameRoom` — owns one `GameEngine` and ticks it on its own asyncio task regardless of whether either player is currently connected; disconnect-grace-then-forfeit timer; reconnect/rejoin; viewer broadcast. |
| `matchmaking.py` | `Matchmaking` — automatic ELO-range pairing queue; gives up (no bot fallback) after a timeout with no human found. |
| `room_registry.py` | Manual create/join/cancel/watch rooms — the human-driven alternative to matchmaking. Both paths build an identical `GameRoom` via the same injected factory. Evicts ended rooms so they don't leak forever. |
| `ws_server.py` | Entrypoint — wires everything above to real `websockets` connections; the only module that touches the `websockets` library directly. |

### `bus/` and `persistence/` — cross-cutting concerns, decoupled via events
| File | What it is |
|---|---|
| `bus/event_bus.py` | `EventBus` — topic-based pub/sub (built on `engine/observer.Subject`) that `GameRoom` publishes every outcome onto, so unrelated subscribers don't need `GameRoom` to know they exist. |
| `persistence/db.py` | SQLite connection + schema bootstrap. |
| `persistence/users_repository.py` | `UsersRepository` — username + ELO, no password. |
| `persistence/elo.py` | Pure ELO rating math, no I/O. |
| `persistence/elo_updater.py` | Bus subscriber: updates both players' ELO when a game between two authenticated users ends. |
| `persistence/event_log.py` | `EventLogWriter` — durable audit trail, one JSONL file per topic. |

### `texttests/` and `main.py`
A tiny domain-specific-language test harness (`script_parser.py`/`script_runner.py`) for
scripting engine behavior as text (`click`, `jump`, `wait`, `print board`) — `server/main.py`
is this same CLI's real entrypoint (reads a board + command script from stdin).

---

## `client/`

### Entry points
| File | What it is |
|---|---|
| `main.py` | The real entrypoint. Open window → login screen → home screen → Play/Rooms over the network → game screen. The render loop itself (`while window.poll(): ...`). |
| `server_bridge.py` | Puts `server/` on `sys.path` so the client can import its pure domain modules (`model`, `rules`, `config`, ...) directly. |
| `dialogs.py` | Real native OS dialogs (tkinter) for Create/Join/Cancel rooms and "no opponent found" popups. |

### `network/` — the WebSocket client side
| File | What it is |
|---|---|
| `ws_client.py` | `WsClient` — runs `websockets` on a background thread, exposes a plain synchronous `send`/`recv_all`/`recv_one_blocking` interface so the (synchronous, non-asyncio) render loop never has to think about asyncio. |
| `network_game_facade.py` | `NetworkGameFacade` — the client-side "the game, over a socket" object. Exposes the *exact same* interface as `state/game_facade.GameFacade`, so every renderer/screen is written once and works for both local and networked play. Keeps its own local `Board`, replaying already-resolved server outcomes onto it — never re-derives what happened, only mirrors it. |

### `state/` — the local-play counterpart, plus shared event/motion machinery
| File | What it is |
|---|---|
| `game_facade.py` | `GameFacade` — wraps an in-process `GameEngine` the same way `NetworkGameFacade` wraps a socket. (Currently unused by `main.py` itself — kept for its own tests and `GameScreen`'s tests — see below.) |
| `game_events.py` | Every UI-facing event dataclass (`MoveAccepted`, `PieceCaptured`, `GameOver`, `OpponentDisconnected`, ...). |
| `motion_tracker.py` | `MotionTracker`/`PendingMotion` — client-side predicted in-flight motion bookkeeping, shared by both facades. Also `chebyshev_distance()`, a tiny shared helper both facades use to size a motion's predicted duration. |
| `outcome_translator.py` | Pure lookup: engine outcome type → UI event type. |
| `observer.py` | `Subject` again (deliberately duplicated from `server/engine/observer.py` — see above). |

### `screens/` — one class per full-window view
| File | What it is |
|---|---|
| `screen_manager.py` | `ScreenManager` — single-slot screen switcher; forwards each frame's tick/render/mouse/key to whichever screen is current. |
| `login_screen.py` | Graphical username entry (the GUI half of the course's "shell or GUI" login choice) — a text box with a blinking cursor, driven by `handle_key`, plus a Login button. |
| `home_screen.py` | Welcome + Play/Rooms buttons. |
| `game_screen.py` | The actual board view — wires together every renderer and every `ui_components/` tracker via the facade's event subscriptions. Takes whichever facade it's given (local or networked) without caring which. |

### `graphics/` — pure rendering, no game logic
| File | What it is |
|---|---|
| `window.py` | Non-blocking window on top of `Img`/cv2 — per-frame polling instead of `Img.show()`'s one-shot blocking call. |
| `sprite_loader.py` | Loads board background + per-piece animated sprites from `assets/`. |
| `piece_renderer.py` | Draws every piece's current animation frame. |
| `overlay_renderer.py` | Draws non-piece overlays (selection, legal-move hints, halt-flash, cooldown-fade, game-over banner) — order is load-bearing (compositing). |
| `renderer.py` | `BoardRenderer` — composes background + pieces + overlays into one frame. |
| `hud_renderer.py` | Adds the White/Black side panels around the rendered board. |
| `protocols.py` | `typing.Protocol` structural types so the renderers above can be unit-tested without real `cv2`/`Img`. |

### `animation/`
| File | What it is |
|---|---|
| `animation_clock.py` | Per-frame delta-time source. |
| `motion_predictor.py` | Turns `(source, destination, progress)` into an actual pixel position for a mid-flight piece. |
| `piece_animator.py` | Per-piece animation state machine (idle/move/jump/short_rest/long_rest), driven by each sprite's `config.json`. |

### `ui_components/` — one small tracker class per HUD concern, each subscribed to `GameFacade`/`NetworkGameFacade`'s events
`cooldown_tracker.py`, `game_over_banner.py`, `halt_flash.py`, `moves_log_panel.py`,
`opponent_status_tracker.py`, `player_labels.py`, `score_panel.py`, `sound_player.py` — each
does exactly one thing (see the module docstrings; they're all short and single-purpose by
design).

### `ui_widgets/`, `user_input/`, misc
| File | What it is |
|---|---|
| `ui_widgets/button.py` | The one clickable widget the `Img`-only rule allows — a labeled rect + hit-test. |
| `ui_widgets/canvas.py` | Blank solid-color canvas for board-less screens (home). |
| `user_input/mouse_controller.py` | Adapts cv2 mouse events to server's `Controller`, plus client-only extras (same-square click = dodge-jump, right-click = jump). |
| `user_settings.py` | User-editable settings (`settings.json`) — skin, names, sound on/off. |
| `ui_config.py` | Internal, not-user-tunable UI constants (colors, pixel offsets, timings). |
| `vendor/img.py` | The course-provided `Img` class, vendored — read-only, never edited. |

---

## Design patterns actually in use (not just named for the sake of it)

- **Observer / Publish-Subscribe** — the backbone of the whole app. `Subject` (duplicated
  once server-side, once client-side, deliberately) lets `GameEngine` and the two client
  facades announce what happened without knowing who's listening. `bus/event_bus.py` is the
  same idea at server scope, with named topics.
- **Facade** — `GameFacade`/`NetworkGameFacade` each wrap a much messier thing (a raw engine,
  a raw socket) behind one clean interface (`request_move`, `snapshot`, `tick`, `subscribe_*`).
- **Duck-typed Strategy / interchangeable backends** — `GameScreen` is handed *either* facade
  and never checks which; both satisfy the same implicit interface. No `ABC`/formal interface
  was introduced for this — deliberately, to match the project's small scope.
- **Repository** — `UsersRepository` hides SQL behind `get_by_username`/`create_user`/etc.
- **Registry** — `RoomRegistry` (manual rooms) and the server's `GameRegistry` (all active
  games, keyed by id) — both just "a live collection of X, keyed by id."
- **Dependency Injection via factories** — `RoomRegistry`/`Matchmaking` both take a
  `new_room` factory function rather than constructing `GameRoom` themselves, so both entry
  paths build identical rooms without duplicating the wiring.
- **Structural typing (Protocol)** — `graphics/protocols.py` lets the rendering layer be unit
  tested without any real `cv2`/`Img` object, by depending on shape, not concrete classes.
- **Translator / pure mapping** — `state/outcome_translator.py` and `net/protocol.py`'s
  dict↔dataclass functions: no state, just "shape A in, shape B out."
- **Single Responsibility, taken seriously** — the biggest structural pattern in this repo
  isn't a GoF pattern at all: almost every file is one small class doing exactly one job
  (compare `piece_renderer.py` vs `overlay_renderer.py` vs `hud_renderer.py`, or the whole
  `ui_components/` folder). `game_screen.py`/`game_facade.py` are themselves mostly just
  *composition roots* — wiring these small pieces together, not implementing logic directly.

## A couple of things worth knowing going in

- **Two "facades" exist, only one is wired up.** `state/game_facade.py`'s `GameFacade` (local,
  in-process, no server needed) is fully implemented and tested, but nothing in `main.py`
  currently builds one — the app always goes over the network. It's kept because
  `GameScreen`'s own tests exercise it directly (a real facade, not a mock, per this
  project's testing style).
- **`server/` never imports from `client/`, ever.** Where both sides need the same small
  primitive (`Subject`), it's copied, not shared — a deliberate call to keep `server/`
  deployable/testable with zero knowledge of the client existing at all.
