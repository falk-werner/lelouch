#!/usr/bin/env python3

from lelouch import Agent, list_models
from openai import OpenAI
import argparse
from os import getenv
import json

def print_usage():
    print("/help             - show this message")
    print("/info             - print current session information")
    print("/history          - prints the history of the current session")
    print("/history pop      - removes the last item from the history")
    print("/models           - list available models")
    print("/model MODEL      - use the model MODEL")
    print("/instruction INST - set instructions (aka system prompt)")
    print("/reasoning VALUE  - set reasoning level (none, minimal, low, high, max)")
    print("/new              - start a new session")
    print("/exit             - exit")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", "-u", type=str, default=getenv("BASE_URL"))
    parser.add_argument("--api-key", "-k", type=str, default=getenv("API_KEY"))
    parser.add_argument("--model", "-m", type=str, default=getenv("MODEL"))
    parser.add_argument("--instructions", "-i", type=str, default="")
    parser.add_argument("--reasoning", "-r", type=str, default=None)
    args = parser.parse_args()
    client = OpenAI(base_url=args.base_url, api_key= args.api_key)

    model = args.model
    instructions = args.instructions
    reasoning = args.reasoning

    agent = Agent(client=client,
        model=model,
        instructions=instructions,
        reasoning=reasoning)

    done = False
    while not done:
        prompt = input(f"{model}> ")
        if prompt == "/exit":
            done = True
        elif prompt == "/help":
            print_usage()
        elif prompt == "/history":
            if len(agent.input_list) == 0:
                print("<empty>")
            else:
                i = 0
                for item in agent.input_list:
                    i += 1
                    print(f"{i}: {item.get("role", "???")}: {item.get("content", "")}")
        elif prompt == "/history pop":
            if len(agent.input_list) > 1:
                agent.input_list = agent.input_list[:-1]
        elif prompt == "/models":
            models = list_models(client)
            for item in models:
                print(item)
        elif prompt == "/new":
            agent = Agent(client=client,
                model=model,
                instructions=instructions,
                reasoning=reasoning)
        elif prompt == "/info":
            print(f"model       : {model}")
            print(f"instructions: {instructions}")
            print(f"reasoning   : {reasoning}")
            print(f"history     : {len(agent.input_list)} items")
        elif prompt.startswith("/model "):
            model = prompt[len("/model "):].strip()
            agent.model = model
        elif prompt.startswith("/instructions "):
            instructions = prompt[len("/instructions "):].strip()
            agent.instructions = instructions
        elif prompt.startswith("/reasoning "):
            reasoning = prompt[len("/reasoning"):].strip()
            agent.reasoning = reasoning
        elif prompt.startswith("/"):
            print("unknown command")
        else:
            agent.execute(prompt)

if __name__ == "__main__":
    main()
