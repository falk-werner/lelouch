
from .tools import Tools
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

    def __init__(self,
            client: OpenAI | None = None,
            model: str | None = None,
            instructions: str = "",
            tools: Tools | None = None):
        self.client = client if client else OpenAI()
        self.model = model if model else getenv_or_die("MODEL")
        self.instructions = instructions
        self.tools = tools if tools else Tools()
        self.input_list = []

    def execute(self, prompt: str):
        self.input_list.append({
            "role": "user",
            "content": prompt
        })

        response = self.client.responses.create(
            model = self.model,
            input = self.input_list,
            instructions = self.instructions,
            tools = self.tools.get()
        )

        print(response.output_text)
        self.input_list.extend(response.output)
