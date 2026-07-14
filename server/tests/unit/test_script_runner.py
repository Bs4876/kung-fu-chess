from texttests.script_parser import ScriptParser
from texttests.script_runner import ScriptRunner


# ── ScriptParser ─────────────────────────────────────────────────────────────

def test_parser_board_command():
    cmds = ScriptParser().parse("Board\nwR . .")
    assert cmds[0] == ("board", "wR . .")


def test_parser_click_command():
    cmds = ScriptParser().parse("Board\nwR . .\nclick 50 50")
    assert ("click", 50, 50) in cmds


def test_parser_wait_command():
    cmds = ScriptParser().parse("Board\nwR . .\nwait 1000")
    assert ("wait", 1000) in cmds


def test_parser_print_board_with_expected():
    cmds = ScriptParser().parse("Board\nwR . .\nprint board\n. wR .")
    assert ("print_board", ". wR .") in cmds


def test_parser_skips_empty_lines():
    cmds = ScriptParser().parse("\nBoard\n\nwR . .\n\nwait 500\n")
    assert cmds[0][0] == "board"
    assert ("wait", 500) in cmds


def test_parser_skips_unknown_lines():
    cmds = ScriptParser().parse("Board\nwR . .\nunknown command here\nwait 100")
    assert ("wait", 100) in cmds


def test_parser_multiple_print_boards():
    cmds = ScriptParser().parse(
        "Board\nwR . .\nwait 1000\nprint board\nwR . .\nwait 1000\nprint board\n. wR ."
    )
    print_cmds = [c for c in cmds if c[0] == "print_board"]
    assert len(print_cmds) == 2
    assert print_cmds[0] == ("print_board", "wR . .")
    assert print_cmds[1] == ("print_board", ". wR .")


# ── ScriptRunner ─────────────────────────────────────────────────────────────

def test_runner_returns_actual_and_expected():
    script = "Board\nwR . .\nwait 1000\nprint board\nwR . ."
    results = ScriptRunner().run(script)
    assert len(results) == 1
    actual, expected = results[0]
    assert actual == "wR . ."
    assert expected == "wR . ."


def test_runner_move_and_print():
    script = "Board\nwR . .\nclick 50 50\nclick 250 50\nwait 2000\nprint board\n. . wR"
    results = ScriptRunner().run(script)
    actual, expected = results[0]
    assert actual == expected == ". . wR"


def test_runner_ignores_click_before_board():
    script = "click 50 50\nBoard\nwR . .\nprint board\nwR . ."
    results = ScriptRunner().run(script)
    actual, _ = results[0]
    assert actual == "wR . ."


def test_runner_ignores_wait_before_board():
    script = "wait 1000\nBoard\nwR . .\nprint board\nwR . ."
    results = ScriptRunner().run(script)
    actual, _ = results[0]
    assert actual == "wR . ."
