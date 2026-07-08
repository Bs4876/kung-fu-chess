import io
import runpy
import sys

import main
from parser import BoardParser
from router import TextCommandRouter
from validator import BoardValidator


class RecordingEngine:
    def __init__(self):
        self.calls = []

    def click(self, x, y):
        self.calls.append(("click", x, y))

    def jump(self, x, y):
        self.calls.append(("jump", x, y))

    def wait(self, ms):
        self.calls.append(("wait", ms))

    def print_board(self):
        self.calls.append(("print",))


def test_board_parser_parses_board_and_commands():
    input_text = """Board:
        wK bQ
        . wP
        Commands:
        click 1 2
        wait 10
    """

    parser = BoardParser()
    board_matrix, command_lines = parser.parse(input_text)

    assert board_matrix == [["wK", "bQ"], [".", "wP"]]
    assert command_lines == ["click 1 2", "wait 10"]


def test_board_validator_accepts_valid_board_structure():
    validator = BoardValidator()
    board_lines = [["wK", "bQ"], [".", "wP"]]

    assert validator.validate_tokens(board_lines) is True
    assert validator.validate_dimensions(board_lines) is True


def test_board_validator_rejects_invalid_tokens_and_dimensions():
    validator = BoardValidator()
    invalid_tokens = [["wK", "bad"], [".", "wP"]]
    inconsistent_dimensions = [["wK", "bQ"], ["."]]

    assert validator.validate_tokens(invalid_tokens) is False
    assert validator.validate_dimensions(inconsistent_dimensions) is False


def test_text_command_router_dispatches_supported_commands():
    engine = RecordingEngine()
    router = TextCommandRouter(engine)

    router.process_command("click 10 20")
    router.process_command("jump 3 4")
    router.process_command("wait 100")
    router.process_command("print board")
    router.process_command("unknown 1 2")
    router.process_command("")

    assert engine.calls == [
        ("click", 10, 20),
        ("jump", 3, 4),
        ("wait", 100),
        ("print",),
    ]


def test_text_command_router_ignores_empty_commands():
    engine = RecordingEngine()
    router = TextCommandRouter(engine)

    router.process_command("")

    assert engine.calls == []


def test_board_validator_handles_empty_input_and_invalid_piece_colors():
    validator = BoardValidator()

    assert validator.validate_tokens([]) is True
    assert validator.validate_dimensions([]) is True
    assert validator.validate_tokens([['xK', '.']]) is False
    assert validator.validate_tokens([['wX', '.']]) is False


def test_main_runs_with_sample_input_without_crashing():
    input_text = """Board:
    wK bQ
    . wP
    Commands:
    print board
    """

    original_stdin = sys.stdin
    original_stdout = sys.stdout
    try:
        sys.stdin = io.StringIO(input_text)
        sys.stdout = io.StringIO()
        main.main()
        output = sys.stdout.getvalue()
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout

    assert "wK bQ" in output


def test_main_returns_for_empty_or_incomplete_input():
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    try:
        sys.stdin = io.StringIO("")
        sys.stdout = io.StringIO()
        main.main()

        sys.stdin = io.StringIO("Board:\nCommands:\n")
        main.main()
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout


def test_module_entrypoint_executes_main():
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    try:
        sys.stdin = io.StringIO("Board:\n wK\nCommands:\nprint board\n")
        sys.stdout = io.StringIO()
        runpy.run_module("main", run_name="__main__")
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout


def test_main_rejects_invalid_row_width():
    input_text = """Board:
    wK . .
    . bK
    Commands:
    """

    original_stdin = sys.stdin
    original_stdout = sys.stdout
    try:
        sys.stdin = io.StringIO(input_text)
        sys.stdout = io.StringIO()
        main.main()
        output = sys.stdout.getvalue()
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout

    assert "ERROR ROW_WIDTH_MISMATCH" in output


def test_main_rejects_unknown_token():
    input_text = """Board:
    wK xZ
    . .
    Commands:
    """

    original_stdin = sys.stdin
    original_stdout = sys.stdout
    try:
        sys.stdin = io.StringIO(input_text)
        sys.stdout = io.StringIO()
        main.main()
        output = sys.stdout.getvalue()
    finally:
        sys.stdin = original_stdin
        sys.stdout = original_stdout

    assert "ERROR UNKNOWN_TOKEN" in output