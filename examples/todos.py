#!/usr/bin/env python3

from lelouch import Agent, Tools, Logger
from openai import OpenAI
import argparse
from os import getenv

import json

todos = []

def add_todo(item: str) -> str:
    """Adds an item to the todo list."""
    todos.append(item)
    return "ok"

def list_todos() -> str:
    """Returns the entire todo list as json array."""
    return json.dumps(todos)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", "-u", type=str, default=getenv("BASE_URL"))
    parser.add_argument("--api-key", "-k", type=str, default=getenv("API_KEY"))
    parser.add_argument("--model", "-m", type=str, default=getenv("MODEL"))
    parser.add_argument("--instructions", "-i", type=str, default="")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("prompt", type=str)
    args = parser.parse_args()

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)
    tools = Tools([add_todo, list_todos])
    log = Logger(use_color=not args.no_color)
    agent = Agent(client=client,
        model=args.model,
        instructions=args.instructions,
        tools=tools,
        log=log)
    agent.execute(args.prompt)

if __name__ == "__main__":
    main()
