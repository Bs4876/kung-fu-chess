class BoardParser:
    def parse(self, input_text):
        lines = [line.strip() for line in input_text.splitlines()]
        
        board_matrix = []
        command_lines = []
        in_board = False

        for line in lines:
            if not line:
                continue
            if line.startswith("Board:"):
                in_board = True
                continue
            elif line.startswith("Commands:"):
                in_board = False
                continue
            
            if in_board:
                board_matrix.append(line.split())
            else:
                # כל שורה שאיננה בלוח ונמצאת מתחת ל-Commands נכנסת כפקודה
                command_lines.append(line)

        return board_matrix, command_lines