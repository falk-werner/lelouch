#!/usr/bin/env python3

from lelouch import Agent, Tools, Logger
from openai import OpenAI
import argparse
from os import getenv

def get_date() -> str:
    """Returns the current date as ISO 8601 string."""
    return "1970-01-01T00:00:00"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", "-u", type=str, default=getenv("BASE_URL"))
    parser.add_argument("--api-key", "-k", type=str, default=getenv("API_KEY"))
    parser.add_argument("--model", "-m", type=str, default=getenv("MODEL"))
    parser.add_argument("--instructions", "-i", type=str, default="")
    parser.add_argument("--reasoning", "-r", type=str, default=None)
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("prompt", type=str)
    args = parser.parse_args()

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)
    tools = Tools([get_date])
    log = Logger(use_color=not args.no_color)
    agent = Agent(client=client,
        model=args.model,
        instructions=args.instructions,
        tools=tools,
        reasoning=args.reasoning,
        log=log)
    agent.execute(args.prompt)

if __name__ == "__main__":
    main()
