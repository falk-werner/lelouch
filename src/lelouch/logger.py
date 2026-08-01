
from typing import Callable

NO_COLOR = ""
YELLOW = '\033[33m'
RED = '\033[31m'
DARK_GRAY = '\033[90m'
RESET = '\033[0m'

class Logger:
    use_color: bool
    printer: Callable

    def __init__(self, use_color=True, printer: Callable | None = None):
        self.use_color = use_color
        self.printer = printer if printer else print

    def _print(self, color: str, message: str):
        if self.use_color:
            self.printer(f"{color}{message}{RESET}")
        else:
            self.printer(message)

    def print(self, message):
        self.printer(message)

    def reason(self, message: str):
        self._print(DARK_GRAY, f"reasoning: {message}")


    def info(self, message: str):
        self._print(DARK_GRAY, f"info: {message}")

    def warn(self, message: str):
        self._print(YELLOW, f"warning: {message}")
