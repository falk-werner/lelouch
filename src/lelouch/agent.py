
from .tools import Tools
from .logger import Logger
from openai import OpenAI
from os import getenv
from typing import List

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
    log: Logger

    def __init__(self,
            client: OpenAI | None = None,
            model: str | None = None,
            instructions: str = "",
            tools: Tools | None = None,
            log: Logger | None = None):
        self.client = client if client else OpenAI()
        self.model = model if model else getenv_or_die("MODEL")
        self.instructions = instructions
        self.tools = tools if tools else Tools()
        self.input_list = []
        self.log = log if log else Logger()

    def execute(self, prompt: str):
        self.input_list.append({
            "role": "user",
            "content": prompt
        })

        done = False
        while not done:
            response = self.client.responses.create(
                model = self.model,
                input = self.input_list,
                instructions = self.instructions,
                tools = self.tools.get(),
            )

            self.input_list.extend(response.output)
            done = True

            for output in response.output:
                if output.type == "function_call":
                    done = False
                    result = self.tools.invoke(output.name, output.arguments, self.log)
                    self.input_list.append({
                        "type": "function_call_output",
                        "call_id": output.call_id,
                        "output": result,
                    })
                elif output.type == "message":
                    for item in output.content:
                        self.log.print(item.text)
                    self.log.info(f"Status: {output.status}")
                elif output.type == "reasoning":
                    for item in output.content:
                        self.log.reason(f"{item.text}")
                else:
                    self.log.warn(f"ignore unsupported output type: {output.type}")

            

        
