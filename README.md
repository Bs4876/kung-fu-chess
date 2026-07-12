# Kung-Fu Chess Server

Modular Python implementation for dynamic chess logic.

## Key Features
- **Clean Architecture:** High modularity with SRP and DRY principles.
- **Quality Assurance:** 100% unit test coverage.
- **Extensibility:** Built with Dependency Injection and a clean command router.

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
Run the project from the repository root:

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
