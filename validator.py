class BoardValidator:
    """
    Responsible for verifying that the board complies with all game rules
    regarding tokens and structural symmetry.
    """
    def __init__(self):
        # Set of valid chess piece characters
        self.valid_pieces = {'K', 'Q', 'R', 'B', 'N', 'P'}

    def validate_tokens(self, board_lines):
        """Checks if all tokens on the board are legal chess pieces or empty spots."""
        for row in board_lines:
            for token in row:
                if token == '.':
                    continue
                # A valid piece must be 2 characters long, start with 'w' or 'b', and end with a valid piece type
                if len(token) != 2 or token[0] not in {'w', 'b'} or token[1] not in self.valid_pieces:
                    return False
        return True

    def validate_dimensions(self, board_lines):
        """Ensures all rows have the exact same width (the board is rectangular)."""
        if not board_lines:
            return True
        
        row_width = len(board_lines[0])
        for row in board_lines:
            if len(row) != row_width:
                return False
        return True