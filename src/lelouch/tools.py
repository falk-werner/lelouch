
from .logger import Logger
from typing import List, Dict, Callable
import inspect
import json

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
        signature = inspect.signature(tool)
        if signature.return_annotation != str:
            raise RuntimeError("return type must be string")
        parameters = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        for param in signature.parameters.values():            
            if param.annotation == str:
                param_type = "string"
            elif param.annotation == bool:
                param_type = "boolean"
            elif param.annotation == int:
                param_type = "integer"
            elif param.annotation == float:
                param_type = "number"
            else:
                raise RuntimeError("parameter type not supported")
            if param.kind != inspect.Parameter.POSITIONAL_OR_KEYWORD and inspect.Parameter.KEYWORD_ONLY:
                raise RuntimeError("only keyword parameters supported")
            
            parameters["properties"][param.name] = { "type": param_type }
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param.name)

        tool_name = name if name else tool.__name__
        doc = {
            "type": "function",
            "name": tool_name,
            "description": tool.__doc__,
        }
        if len(parameters["properties"]) > 0:
            doc["parameters"] = parameters

        self.tools[tool_name] = tool
        self.docs.append(doc)

    def invoke(self, tool_name: str, arguments: str, log: Logger) -> str:
        log.info(f"Model wants to call tool {tool_name} with arguments {arguments}")
        tool = self.tools.get(tool_name)
        if tool:
            args = ()
            kwargs = json.loads(arguments)
            return tool(*args, **kwargs)
        log.warn(f"unknown tool {tool_name}")
        return "error: unknown tool"

    def get(self):
        return self.docs