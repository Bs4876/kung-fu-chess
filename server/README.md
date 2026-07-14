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
Run the project from this `server/` directory:

```bash
python main.py < input.txt
```

The program reads the board definition and commands from standard input.

## Testing
Run the full unit test suite with coverage:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

## Notes
- Avoid using `monkeypatch` in unit tests; prefer dependency injection.
- Keep business rules configurable and avoid hard-coded game logic where possible.
- The code is designed to support future extension of custom piece movement rules.
