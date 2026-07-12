from chess_io.board_parser import BoardParser
from chess_io.board_printer import BoardPrinter
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper
from input.controller import Controller
from texttests.script_parser import ScriptParser
from config import CELL_SIZE


class ScriptRunner:
    def __init__(self):
        self._parser = BoardParser()
        self._printer = BoardPrinter()
        self._script_parser = ScriptParser()

    def run(self, script_text: str) -> list[str]:
        commands = self._script_parser.parse(script_text)
        results = []
        engine = None
        controller = None

        for cmd in commands:
            if cmd[0] == "board":
                board = self._parser.parse(cmd[1])
                engine = GameEngine(board)
                mapper = BoardMapper(rows=board.rows, cols=board.cols, cell_size=CELL_SIZE)
                controller = Controller(engine, mapper)
            elif cmd[0] == "click" and controller:
                controller.click(cmd[1], cmd[2])
            elif cmd[0] == "wait" and engine:
                engine.wait(cmd[1])
            elif cmd[0] == "print_board" and engine:
                snap = engine.snapshot()
                actual = self._printer.print(snap)
                expected = cmd[1]
                results.append((actual, expected))

        return results
