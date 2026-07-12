from chess_io.board_parser import BoardParser
from chess_io.board_printer import BoardPrinter


def roundtrip(text):
    board = BoardParser().parse(text)
    return BoardPrinter().print(board)


def test_single_row_roundtrip():
    assert roundtrip("wK . bK") == "wK . bK"


def test_multi_row_roundtrip():
    assert roundtrip("wK . .\n. . .\n. . bK") == "wK . .\n. . .\n. . bK"


def test_all_empty_board():
    assert roundtrip(". . .\n. . .") == ". . .\n. . ."


def test_all_piece_kinds_roundtrip():
    assert roundtrip("wK wQ wR wB wN wP") == "wK wQ wR wB wN wP"


def test_black_pieces_roundtrip():
    assert roundtrip("bK bQ bR bB bN bP") == "bK bQ bR bB bN bP"


def test_rectangular_board_roundtrip():
    assert roundtrip("wR . . bR\n. . . .") == "wR . . bR\n. . . ."
