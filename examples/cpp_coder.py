#!/usr/bin/env python3

from lelouch import Agent, Tools
from openai import OpenAI
import argparse
import os
import readline
import json
import subprocess

workspace = None

def list_files(directory: str = "/") -> str:
    """Recursively lists files in a directory as json list."""
    base_dir = os.path.realpath(os.path.join(workspace, directory.lstrip("/")))

    result = []
    if os.path.commonpath([workspace, base_dir]) != workspace:
        return json.dumps(result)

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(base_dir, root, file)
            if os.path.isfile(full_path):
                result.append(os.path.relpath(full_path, base_dir))
    return json.dumps(result)
        
    
def file_read(filename: str) -> str:
    """Returns the full contents of a file."""
    full_filename =os.path.realpath(os.path.join(workspace, filename.lstrip("/")))

    if os.path.commonpath([workspace, full_filename]) != workspace:
        return "error: path traversal detected"

    if not os.path.isfile(full_filename):
        return "error: file not found"
    
    with open(full_filename, "r", encoding="utf-8") as f:
        return f.read()

def file_write(filename: str, contents: str) -> str:
    """Writes the contents of a file."""
    full_filename =os.path.realpath(os.path.join(workspace, filename.lstrip("/")))

    if os.path.commonpath([workspace, full_filename]) != workspace:
        return "error: path traversal detected"

    with open(full_filename, "w", encoding="utf-8") as f:
        f.write(contents)

    return "ok"

def cmake_configure() -> str:
    """Configures a cmake project."""
    result = subprocess.run(["cmake", "-B", "build"], cwd=workspace, capture_output=True, text=True)
    return json.dumps({
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    })

def cmake_build() -> str:
    """
    Builds a CMake project.

    Project must be configured before it can be build.
    """
    result = subprocess.run(["cmake", "--build", "build"], cwd=workspace, capture_output=True, text=True)
    return json.dumps({
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    })

def main():
    global workspace

    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", "-u", type=str, default=os.getenv("BASE_URL"))
    parser.add_argument("--api-key", "-k", type=str, default=os.getenv("API_KEY"))
    parser.add_argument("--model", "-m", type=str, default=os.getenv("MODEL"))
    parser.add_argument("--instructions", "-i", type=str, default="")
    parser.add_argument("--reasoning", "-r", type=str, default=None)
    parser.add_argument("workspace", type=str)
    args = parser.parse_args()

    if not os.path.isdir(args.workspace):
        print("error: workspace must be existing directory")
        exit(1)
    workspace = os.path.realpath(args.workspace)

    client = OpenAI(base_url=args.base_url, api_key= args.api_key)

    agent = Agent(client=client,
        model=args.model,
        instructions=args.instructions,
        reasoning=args.reasoning,
        tools=Tools([file_read, list_files, file_write, cmake_configure, cmake_build]))

    done = False
    while not done:
        prompt = input(f"{args.model}> ")
        if prompt == "/exit":
            done = True
        else:
            agent.execute(prompt)


if __name__ == "__main__":
    main()
