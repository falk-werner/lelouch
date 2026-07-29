
from typing import List, Callable

class Tools:
    tools: List

    def __init__(self):
        self.tools = []

    def add(self, tool: Callable, name: str | None = None, ask: bool = True):
        # ToDo: add tool to tools struct
        pass

    def invoke(self, tool: str, arguments) -> str:
        # ToDo: invoke tool
        pass

    def get(self):
        return self.tools