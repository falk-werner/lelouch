
from ..user_interaction import UserInteraction
from typing import List, Dict, Callable
import inspect
import json

class Tools:
    docs: List
    tools: Dict
    ask: Dict[bool]

    def __init__(self, tools: List | None = None):
        self.docs = []
        self.tools = {}
        self.ask = {}
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
        self.ask[tool_name] = ask
        self.docs.append(doc)

    def invoke(self, tool_name: str, arguments: str, user_interaction: UserInteraction) -> str:
        arguments=json.loads(arguments)
        ask = self.ask.get(tool_name, True)
        if ask:
            permitted = user_interaction.ask(f"Model wants to call a tool:\n  name: {tool_name}\n  args: {json.dumps(arguments,indent=4)}\n\nPermit? [Y for yes, A for always, N for no or reason to reject]: ")
            if permitted in ["", "N", "n"]:
                return f"error: tool usage not permitted by user"
            if permitted not in ["Y", "y", "A", "a"]:
                return f"error: tool usage not permitted by user: {permitted}"
            if permitted in ["A", "a"]:
                confirmed = user_interaction.ask(f"Do you really want to permit each usage of this tool? [Y/N]: ")
                if confirmed in ["Y", "y"]:
                    self.ask[tool_name] = False
        else:
            user_interaction.info(f"Model calls permitted tool {tool_name} with arguments {json.dumps(arguments, indent=4)}.")

        tool = self.tools.get(tool_name)
        if tool:
            args = ()
            kwargs = arguments
            return tool(*args, **kwargs)
        user_interaction.warn(f"unknown tool {tool_name}")
        return "error: unknown tool"

    def get(self):
        return self.docs

class BaseTool:
    name: str

    def __init__(self, name: str):
        self.name = name

    def __getattr__(self, name: str):
        if name == "__name__":
            return self.name
        else:
            raise AttributeError
