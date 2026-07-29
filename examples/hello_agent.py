#!/usr/bin/env python3

from lelouch import Agent
from openai import OpenAI
import argparse
from os import getenv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", "-u", type=str, default=getenv("BASE_URL"))
    parser.add_argument("--api-key", "-k", type=str, default=getenv("API_KEY"))
    parser.add_argument("--model", "-m", type=str, default=getenv("MODEL"))
    parser.add_argument("--instructions", "-i", type=str, default="")
    parser.add_argument("prompt", type=str)
    args = parser.parse_args()
    client = OpenAI(base_url=args.base_url, api_key= args.api_key)    
    agent = Agent(client=client, model=args.model, instructions=args.instructions)
    agent.execute(args.prompt)

if __name__ == "__main__":
    main()