
from .tools import BaseTool

import os
import json
import fnmatch

from typing import List

class BaseFileTool(BaseTool):
    """
    Abstract base class of file tools.

    Use to create own additional file tools.
    Not intendet to be used by AI directly.
    """

    workdir: str
    ignored_files: List[str]

    def __init__(self, workdir: str, name: str, ignored_files: List[str] | None = None):
        super(BaseFileTool, self).__init__(name)
        self.workdir = workdir
        self.ignored_files = ignored_files if ignored_files else [".*", "**/.*"]

    def resolve(self, path: str) -> str:
        resolved_path = os.path.realpath(os.path.join(self.workdir, path.lstrip("/")))

        if os.path.commonpath([self.workdir, resolved_path]) != self.workdir:
            raise RuntimeError("path traversal detected")

        return resolved_path

    def is_ignored(self, name: str) -> bool:
        for pattern in self.ignored_files:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False


class RemoveFileTool(BaseFileTool):
    """
    Removes a single file.
    
    Returns "ok" on success.
    """

    def __init__(self, workdir: str,
            name: str = "remove_file",
            ignored_files : List[str] | None = None):
        super(RemoveFileTool, self).__init__(workdir, name, ignored_files)

    def __call__(self, filename: str) -> str:
        if not isinstance(filename, str):
            return "error: invalid arguments"

        try:
            resolved_filename = self.resolve(filename)
        except Exception:
            return "error: invalid filename"

        relative_filename = os.path.relpath(resolved_filename, self.workdir)
        if not os.path.exists(resolved_filename) or self.is_ignored(relative_filename):
            return "ok"
        
        if not os.path.isfile(resolved_filename):
            return "error: not a file"

        try:
            os.remove(resolved_filename)
        except Exception:
            return "error: failed to remove file"

        return "ok"

class ListFilesTool(BaseFileTool):
    """
    Recusively lists files in a directory.

    Returns a list of files as json array on success.
    Returns an error message on failure.
    """

    def __init__(self, workdir: str,
            name: str = "list_files",
            ignored_files: List[str] | None = None):
        super(ListFilesTool, self).__init__(workdir, name, ignored_files)

    def __call__(self, directory: str = "/") -> str:
        if not isinstance(directory, str):
            return "error: invalid arguments"

        try:
            resolved_directory = self.resolve(directory)
        except Exception:
            return "error: invalid directory"

        if not os.path.isdir(resolved_directory):
            return "error: directory not found or not a directory"

        result = []
        for root, dirs, files in os.walk(resolved_directory):
            for file in files:
                full_path = os.path.join(resolved_directory, root, file)

                if not os.path.isfile(full_path) or os.path.islink(full_path):
                    continue

                relative_filename = os.path.relpath(full_path, self.workdir)
                if self.is_ignored(relative_filename):
                    continue

                result.append(relative_filename)

        return json.dumps(result)

class ReadFileTool(BaseFileTool):
    """
    Reads the contents of a file.

    Arguments:
    - `filename`: name of the file to read
    - `first_line`: first line to read. Default: 0 (first line)
    - `line_count`: amount of lines to read. Default: 0 (read whole file)

    Return a json object.

    On success, the property `first_line` contains the number of the first line read,
    the property `total_lines` contains the total amount of lines in the file and the
    property `lines` contains the array of the lines read from the file.
    Example: `{"first_line": 0, "total_lines": 2, "lines": ["first line", "second line"]}`

    On failure, the error message is return in the `error` property.
    Example: `{"error": "error message"}`
    """

    def __init__(self, workdir: str,
            name: str = "read_file",
            ignored_files: List[str] | None = None):
        super(ReadFileTool, self).__init__(workdir, name, ignored_files)

    def __call__(self, filename: str, first_line: int = 0, line_count: int = 0) -> str:
        if not isinstance(filename, str) or not isinstance(first_line, int) \
                or not isinstance(line_count, int) or first_line < 0 or line_count < 0:
            return json.dumps({"error": "invalid arguments"})

        try:
            resolved_filename = self.resolve(filename)
        except Exception:
            return json.dumps({"error": "invalid filename"})

        relative_filename = os.path.relpath(resolved_filename, self.workdir)
        if not os.path.exists(resolved_filename) or self.is_ignored(relative_filename):
            return json.dumps({"error": "file not found"})

        if not os.path.isfile(resolved_filename):
            return json.dumps({"error": "not a file"})

        try:
            with open(resolved_filename,"r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return json.dumps({"error": "failed to read file"})

        total_lines = len(lines)
        if line_count == 0:
            lines = lines[first_line:]
        else:
            lines = lines[first_line: first_line + line_count]

        return json.dumps({"first_line": first_line, "total_lines": total_lines, "lines": lines}) 