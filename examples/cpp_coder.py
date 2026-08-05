#!/usr/bin/env python3

from lelouch import Agent, Tools
from openai import OpenAI
import argparse
import os
import readline
import json
import subprocess
import tempfile

workspace = None
build_dir = None

def resolve(path: str) -> str:
    resolved_path = os.path.realpath(os.path.join(workspace, path.lstrip("/")))

    if os.path.commonpath([workspace, resolved_path]) != workspace:
        raise RuntimeError("path traversal detected")

    return resolved_path


def file_remove(filename: str) -> str:
    """Removes a single file."""
    full_filename = resolve(filename)

    if not os.path.isfile(full_filename):
        return "error: not a file"
    
    os.remove(full_filename)
    return "ok"

def list_files(directory: str = "/") -> str:
    """Recursively lists files in a directory as json list."""
    base_dir = resolve(directory)

    result = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(base_dir, root, file)

            # skip hidden files an directories
            if "/." in full_path:
                continue

            if os.path.isfile(full_path):
                result.append(os.path.relpath(full_path, base_dir))

    return json.dumps(result)
        
    
def file_read(filename: str) -> str:
    """Returns the full contents of a file."""
    full_filename = resolve(filename)

    if not os.path.isfile(full_filename):
        return "error: file not found"
    
    with open(full_filename, "r", encoding="utf-8") as f:
        return f.read()

def file_create(filename: str, contents: str) -> str:
    """
    Creates a new file with the given contents.
    If the parent dir does not exist, it will be created.
    Should not be used to edit already existing files.
    """
    full_filename = resolve(filename)

    parent_dir = os.path.dirname(full_filename)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir)

    with open(full_filename, "w", encoding="utf-8") as f:
        f.write(contents)
    return "ok"

def file_rename(source: str, target: str) -> str:
    """Renames the file or directory source to target."""
    full_source = resolve(source)
    full_target = resolve(target)

    os.rename(full_source, full_target)
    return "ok"

def file_replace_string(filename: str, old: str, new: str) -> str:
    """
    Replaces a single occurece of the string `old` by `new` in the file `filename`.
    Use this tool to edit existing files.
    """
    full_filename = resolve(filename)

    try:
        with open(full_filename, "r", encoding="utf-8") as f:
            contents = f.read()
    except Exception:
        return "error: failed to read file"

    count = contents.count(old)
    if count == 1:
        contents = contents.replace(old, new)
        with open(full_filename, "w", encoding="utf-8") as f:
            f.write(contents)
        return "ok"
    elif count == 0:
        return "error: cannot find `old` in file."
    else:
        return "error: found `old` multiple times in file; please add more context."


def cmake_configure() -> str:
    """Configures a cmake project."""
    result = subprocess.run(["cmake", "-B", build_dir], cwd=workspace, capture_output=True, text=True)
    if result.returncode == 0:
        return json.dumps({"returncode": 0, "stdout": "", "stderr": ""})
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
    result = subprocess.run(["cmake", "--build", build_dir], cwd=workspace, capture_output=True, text=True)
    if result.returncode == 0:
        return json.dumps({"returncode": 0})
    return json.dumps({
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    })

def cmake_test() -> str:
    """
    Runs all unit tests.
    
    Project must be build before running the tests.
    """
    result = subprocess.run(["cmake", "--build", build_dir, "--target", "test"], cwd=workspace, capture_output=True, text=True)
    if result.returncode == 0:
        return json.dumps({"returncode": 0})
    return json.dumps({
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    })



def new_agent(client, args) -> Agent:
    return Agent(client=client,
        model=args.model,
        instructions=args.instructions,
        reasoning=args.reasoning,
        tools=Tools([file_read, list_files, file_create, file_remove, file_rename, file_replace_string,
                     cmake_configure, cmake_build, cmake_test]))


def main():
    global workspace
    global build_dir

    DEFAULT_INSTRUCTION="""
    You are a skilled C++ programmer. You assist in creating C++ applications
    using C++ 17, CMake and Google Test. You use the provided tools for doing so.
    Keep your answers short and precise.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", "-u", type=str, default=os.getenv("BASE_URL"))
    parser.add_argument("--api-key", "-k", type=str, default=os.getenv("API_KEY"))
    parser.add_argument("--model", "-m", type=str, default=os.getenv("MODEL"))
    parser.add_argument("--instructions", "-i", type=str, default=DEFAULT_INSTRUCTION)
    parser.add_argument("--reasoning", "-r", type=str, default=None)
    parser.add_argument("--build-dir", "-b", type=str, default=None)
    parser.add_argument("workspace", type=str)
    args = parser.parse_args()

    if not os.path.isdir(args.workspace):
        print("error: workspace must be existing directory")
        exit(1)
    workspace = os.path.realpath(args.workspace)

    build_dir = args.build_dir
    if args.build_dir == None:
        build_dir = tempfile.TemporaryDirectory(prefix="lelouch_builddir_").name
        print(f"build dir: {build_dir}")

    client = OpenAI(base_url=args.base_url, api_key= args.api_key)
    agent = new_agent(client, args)

    done = False
    while not done:
        prompt = input(f"{args.model}> ")
        if prompt == "/exit":
            done = True
        elif prompt == "/new":
            agent = new_agent(client, args)
        else:
            agent.execute(prompt)


if __name__ == "__main__":
    main()
