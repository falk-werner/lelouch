
from .tools import Tools
from .user_interaction import UserInteraction
from openai import OpenAI, omit
from os import getenv
from typing import List
import json

def getenv_or_die(name):
    result = getenv(name)
    if result == None:
        raise RuntimeError(f"missing required environment variable {name}")

class Agent:
    client: OpenAI
    model: str
    instructions: str
    tools: Tools
    input_list: List
    reasoning: bool
    user_interaction: UserInteraction

    def __init__(self,
            client: OpenAI | None = None,
            model: str | None = None,
            instructions: str = "",
            tools: Tools | None = None,
            reasoning: bool | str | None = None,
            user_interaction: UserInteraction | None = None):
        self.client = client if client else OpenAI()
        self.model = model if model else getenv_or_die("MODEL")
        self.instructions = instructions
        self.tools = tools if tools else Tools()
        self.input_list = []
        self.reasoning = reasoning
        self.user_interaction = user_interaction if user_interaction else UserInteraction()

    def execute(self, prompt: str):
        self.input_list.append({
            "role": "user",
            "content": prompt
        })

        if isinstance(self.reasoning, bool):
            reasoning = {"effort": "medium"} if self.reasoning else {"effort": "none"}
        elif isinstance(self.reasoning, str):
            reasoning = {"effort": self.reasoning}
        else:
            reasoning = omit
   
        done = False
        while not done:
            response = self.client.responses.create(
                model = self.model,
                input = self.input_list,
                instructions = self.instructions,
                tools = self.tools.get(),
                reasoning = reasoning
            )

            for output in response.output:
                self.input_list.append(output.to_dict())
            done = True

            for output in response.output:
                if output.type == "function_call":
                    done = False

                    try:
                        result = self.tools.invoke(output.name, output.arguments, self.user_interaction)
                        if not isinstance(result, str):
                            raise RuntimeError("invalid result type")
                        try:
                            self.user_interaction.info(f"tool result: {json.dumps(json.loads(result), indent=4)}")
                        except Exception:
                            self.user_interaction.info(f"tool result: {result}")
                    except Exception as ex:
                        self.user_interaction.warn(f"error calling tools: {ex}")
                        result = "error"

                    self.input_list.append({
                        "type": "function_call_output",
                        "call_id": output.call_id,
                        "output": result,
                    })
                elif output.type == "message":
                    for item in output.content:
                        self.user_interaction.print(item.text)
                    self.user_interaction.info(f"Status: {output.status}")
                elif output.type == "reasoning":
                    for item in output.content:
                        self.user_interaction.reason(f"{item.text}")
                else:
                    self.user_interaction.warn(f"ignore unsupported output type: {output.type}")

            

        
