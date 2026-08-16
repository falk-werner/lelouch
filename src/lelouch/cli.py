#!/usr/bin/env python3

import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", "-w", type=str, default=".")
    parser.add_argument("script", type=str)
    parser.add_argument("args",type=str, nargs="*")
    args = parser.parse_args()
    subprocess.call([args.script])


if __name__ == "__main__":
    main()
