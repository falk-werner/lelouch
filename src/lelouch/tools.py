
from .logger import Logger
from typing import List, Dict, Callable

class Tools:
    docs: List
    tools: Dict

    def __init__(self, tools: List | None = None):
        self.tools = {}
        self.docs = []
        if tools:
            for tool in tools:
                if isinstance(tool, Callable):
                    self.add(tool)
                else:
                    self.add(tool=tool.get("tool"), name=tool.get("name"), ask=tool.get("ask"))

    def add(self, tool: Callable, name: str | None = None, ask: bool = True):
        tool_name = name if name else tool.__name__
        self.tools[tool_name] = tool
        self.docs.append({
            "type": "function",
            "name": tool_name,
            "description": tool.__doc__,
        })

    def invoke(self, tool_name: str, arguments: str, log: Logger) -> str:
        log.info(f"Model wants to call tool {tool_name} with arguments {arguments}")
        tool = self.tools.get(tool_name)
        if tool:
            return tool()
        log.warn(f"unknown tool {tool_name}")
        return "error: unknown tool"

    def get(self):
        return self.docs