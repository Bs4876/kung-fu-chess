# Repository URL: https://github.com/Bs4876/kung-fu-chess-server

import sys
from engine import ChessEngine
from parser import BoardParser
from router import TextCommandRouter
from validator import BoardValidator

def main():
    # Read all input from standard input
    input_text = sys.stdin.read().strip()
    if not input_text:
        return

    parser = BoardParser()
    board_matrix, command_lines = parser.parse(input_text)

    if not board_matrix:
        return

    # Validate the board before creating the engine
    validator = BoardValidator()
    
    if not validator.validate_dimensions(board_matrix):
        print("ERROR ROW_WIDTH_MISMATCH")
        return
    
    if not validator.validate_tokens(board_matrix):
        print("ERROR UNKNOWN_TOKEN")
        return

    engine = ChessEngine(board_matrix)
    router = TextCommandRouter(engine)

    for command in command_lines:
        router.process_command(command)

if __name__ == "__main__":
    main()