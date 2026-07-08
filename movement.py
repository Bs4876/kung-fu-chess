from constants import EMPTY_CELL, WHITE, BLACK

class MoveValidator:
    @staticmethod
    def is_valid_move(piece_type, from_row, from_col, to_row, to_col, board, piece_color):
        if from_row == to_row and from_col == to_col:
            return False

        validator = MoveValidator._VALIDATORS.get(piece_type)
        if validator is None:
            return False

        return validator(from_row, from_col, to_row, to_col, board, piece_color)

    @staticmethod
    def _validate_pawn(from_row, from_col, to_row, to_col, board, piece_color):
        d_col = abs(to_col - from_col)
        row_diff = to_row - from_row
        target_token = board.get_piece(to_row, to_col)
        forward_direction = -1 if piece_color == WHITE else 1
        start_row = board.rows - 1 if piece_color == WHITE else 0

        if d_col == 0:
            if row_diff == forward_direction:
                return target_token == EMPTY_CELL
            if row_diff == 2 * forward_direction and from_row == start_row:
                if target_token != EMPTY_CELL:
                    return False
                return MoveValidator._is_path_clear(from_row, from_col, to_row, to_col, board)
            return False

        if d_col == 1 and row_diff == forward_direction:
            return target_token != EMPTY_CELL

        return False

    @staticmethod
    def _validate_king(from_row, from_col, to_row, to_col, board, piece_color):
        d_row = abs(to_row - from_row)
        d_col = abs(to_col - from_col)
        return d_row <= 1 and d_col <= 1

    @staticmethod
    def _validate_knight(from_row, from_col, to_row, to_col, board, piece_color):
        d_row = abs(to_row - from_row)
        d_col = abs(to_col - from_col)
        return (d_row == 2 and d_col == 1) or (d_row == 1 and d_col == 2)

    @staticmethod
    def _validate_rook(from_row, from_col, to_row, to_col, board, piece_color):
        d_row = abs(to_row - from_row)
        d_col = abs(to_col - from_col)
        if d_row != 0 and d_col != 0:
            return False
        return MoveValidator._is_path_clear(from_row, from_col, to_row, to_col, board)

    @staticmethod
    def _validate_bishop(from_row, from_col, to_row, to_col, board, piece_color):
        d_row = abs(to_row - from_row)
        d_col = abs(to_col - from_col)
        if d_row != d_col:
            return False
        return MoveValidator._is_path_clear(from_row, from_col, to_row, to_col, board)

    @staticmethod
    def _validate_queen(from_row, from_col, to_row, to_col, board, piece_color):
        d_row = abs(to_row - from_row)
        d_col = abs(to_col - from_col)
        if d_row == 0 or d_col == 0 or d_row == d_col:
            return MoveValidator._is_path_clear(from_row, from_col, to_row, to_col, board)
        return False

    _VALIDATORS = {
        'P': _validate_pawn,
        'K': _validate_king,
        'N': _validate_knight,
        'R': _validate_rook,
        'B': _validate_bishop,
        'Q': _validate_queen,
    }

    @staticmethod
    def _is_path_clear(from_row, from_col, to_row, to_col, board):
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)

        curr_row = from_row + row_step
        curr_col = from_col + col_step

        while curr_row != to_row or curr_col != to_col:
            if board.get_piece(curr_row, curr_col) != EMPTY_CELL:
                return False
            curr_row += row_step
            curr_col += col_step

        return True