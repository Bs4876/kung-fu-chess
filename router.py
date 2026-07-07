class TextCommandRouter:
    """
    Decouples raw text commands from the game engine logic by routing
    parsed instructions directly to their corresponding methods.
    """
    def __init__(self, engine):
        self.engine = engine
        # Map text keys directly to target execution handlers
        self.dispatch_map = {
            "click": self._handle_click,
            "wait": self._handle_wait,
            "print": self._handle_print
        }

    def process_command(self, command_line):
        """Tokenizes a command line and triggers the matching application logic."""
        parts = command_line.split()
        if not parts:
            return

        action = parts[0]
        if action in self.dispatch_map:
            self.dispatch_map[action](parts[1:])

    def _handle_click(self, args):
        x, y = int(args[0]), int(args[1])
        self.engine.click(x, y)

    def _handle_wait(self, args):
        ms = int(args[0])
        self.engine.wait(ms)

    def _handle_print(self, args):
        if args and args[0] == "board":
            self.engine.print_board()