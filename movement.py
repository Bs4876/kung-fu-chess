class MoveValidator:
    @staticmethod
    def is_valid_move(piece_type, from_row, from_col, to_row, to_col, board):
        # Remaining in the exact same spot is an illegal operation
        if from_row == to_row and from_col == to_col:
            return False

        # Calculate absolute vector deltas
        d_row = abs(to_row - from_row)
        d_col = abs(to_col - from_col)

        # Step 1: Geometry Check (From Iteration 3)
        is_geometry_valid = False
        if piece_type == 'K':
            is_geometry_valid = d_row <= 1 and d_col <= 1
        elif piece_type == 'R':
            is_geometry_valid = d_row == 0 or d_col == 0
        elif piece_type == 'B':
            is_geometry_valid = d_row == d_col
        elif piece_type == 'Q':
            is_geometry_valid = (d_row == 0 or d_col == 0) or (d_row == d_col)
        elif piece_type == 'N':
            is_geometry_valid = (d_row == 2 and d_col == 1) or (d_row == 1 and d_col == 2)

        if not is_geometry_valid:
            return False

        # Step 2: Path Obstruction Check (New for Iteration 4)
        # Knight ('N') can jump over pieces, King ('K') moves only 1 square (no path to obstruct)
        if piece_type in ['K', 'N']:
            return True

        return MoveValidator._is_path_clear(from_row, from_col, to_row, to_col, board)

    @staticmethod
    def _is_path_clear(from_row, from_col, to_row, to_col, board):
        # Determine the direction step (-1, 0, or 1) for rows and columns
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)

        curr_row = from_row + row_step
        curr_col = from_col + col_step

        # Scan the squares strictly between the start and destination points
        while curr_row != to_row or curr_col != to_col:
            if board[curr_row][curr_col] != '.':
                return False  # Path is blocked by another piece
            curr_row += row_step
            curr_col += col_step

        return True