class ScriptParser:
    def parse(self, text: str) -> list[tuple]:
        commands = []
        lines = [line.strip() for line in text.splitlines()]
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line:
                i += 1
                continue
            parts = line.split()
            if parts[0] == "Board":
                board_lines = []
                i += 1
                while i < len(lines) and lines[i] and lines[i].split()[0] not in ("click", "wait", "print"):
                    board_lines.append(lines[i])
                    i += 1
                commands.append(("board", "\n".join(board_lines)))
            elif parts[0] == "click" and len(parts) == 3:
                commands.append(("click", int(parts[1]), int(parts[2])))
                i += 1
            elif parts[0] == "wait" and len(parts) == 2:
                commands.append(("wait", int(parts[1])))
                i += 1
            elif parts[0] == "print" and len(parts) == 2 and parts[1] == "board":
                expected_lines = []
                i += 1
                while i < len(lines) and lines[i] and lines[i].split()[0] not in ("click", "wait", "print", "Board"):
                    expected_lines.append(lines[i])
                    i += 1
                commands.append(("print_board", "\n".join(expected_lines)))
            else:
                i += 1
        return commands
