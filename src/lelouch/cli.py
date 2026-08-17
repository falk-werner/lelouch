#!/usr/bin/env python3

import argparse
import subprocess
import sys
from importlib.metadata import version
import tempfile
import os
import shutil

DOCKERFILE = """
FROM python:3.14-alpine

RUN pip install openai lelouch

COPY /src /lelouch/src
COPY /pyproject.toml /lelouch

RUN cd /lelouch && python3 -m pip install .

WORKDIR /workspace

ENTRYPOINT [ "python3", "/agent/agent.py" ]
"""

PYPROJECT_TOML = """
[build-system]
requires = ["setuptools >= 77.0.3"]
build-backend = "setuptools.build_meta"

[project]
name = "lelouch"
version = "<VERSION>"
dependencies = [
  "openai>=2.50.0",
]
"""

def get_version() -> str:
    try:
        return version("lelouch")
    except:
        return "snapshot"

def has_docker() -> bool:
    result = subprocess.run(["which", "docker"],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    return result.returncode == 0

def docker_image_exists(name: str) -> bool:
    result = subprocess.run(["docker", "image", "ls", name, "--format", "json"], 
        check=True, capture_output=True, text=True)
    return result.stdout != ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", "-u", type=str, default=os.getenv("BASE_URL"))
    parser.add_argument("--api-key", "-k", type=str, default=os.getenv("API_KEY"))
    parser.add_argument("--model", "-m", type=str, default=os.getenv("MODEL"))
    parser.add_argument("--user", "-U", type=int, default=os.getuid())
    parser.add_argument("--group", "-G", type=int, default=os.getgid())
    parser.add_argument("--workspace", "-w", type=str, default=".")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("script", type=str)
    parser.add_argument("args",type=str, nargs="*")
    args = parser.parse_args()
    # print(__file__)

    if not has_docker():
        print("error: docker binary not found",file=sys.stderr)
        return 1

    image_name = f"lelouch:{get_version()}"
    if not docker_image_exists(image_name) or args.rebuild:
        with tempfile.TemporaryDirectory(prefix="lelouch_", delete=True) as workdir:
            # module_dir = os.path.join(workdir, "src", "lelouch")
            # os.makedirs(module_dir)
            with open(os.path.join(workdir, "Dockerfile"), "w", encoding="utf-8") as f:
                f.write(DOCKERFILE)

            with open(os.path.join(workdir, "pyproject.toml"), "w", encoding="utf-8") as f:
                f.write(PYPROJECT_TOML.replace("<VERSION>", get_version()))

            shutil.copyfile(args.script, os.path.join(workdir, "agent.py"))

            module_dir = os.path.dirname(__file__)
            for root, _, files in os.walk(module_dir):
                for file in files:
                    if not file.endswith(".py"):
                        continue
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(workdir, "src", "lelouch", os.path.relpath(source_file, module_dir))
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    shutil.copyfile(source_file, target_file)

            result = subprocess.call(["docker", "build", "-t", image_name, "."], cwd=workdir)
            if result != 0:
                print("error: failed to build leloch sandbox image",file=sys.stderr)
                return 1

    cmd = [
        "docker", "run", "-it", "--rm",
        "--user", f"{args.user}:{args.group}",
        "-e", f"BASE_URL={args.base_url}",
        "-e", f"API_KEY={args.api_key}",
        "-e", f"MODEL={args.model}",
        "-v", f"{os.path.realpath(args.script)}:/agent/agent.py",
        "-v", f"{os.path.realpath(args.workspace)}:/workspace",
        image_name,
    ]
    cmd.extend(args.args)
    return subprocess.call(cmd)

if __name__ == "__main__":
    main()
