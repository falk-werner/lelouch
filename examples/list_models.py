#!/usr/bin/env python3

from lelouch import list_models
from openai import OpenAI
import argparse
from os import getenv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", "-u", type=str, default=getenv("BASE_URL"))
    parser.add_argument("--api-key", "-k", type=str, default=getenv("API_KEY"))
    args = parser.parse_args()
    client = OpenAI(base_url=args.base_url, api_key=args.api_key)
    for model in list_models(client):
        print(model)

if __name__ == "__main__":
    main()
