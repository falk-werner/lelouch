
import os
from .tools import BaseTool

def resolve(workdir: str, path: str) -> str:
    resolved_path = os.path.realpath(os.path.join(workdir, path.lstrip("/")))

    if os.path.commonpath([workdir, resolved_path]) != workdir:
        raise RuntimeError("path traversal detected")

    return resolved_path

class RemoveFileTool(BaseTool):
    """
    Removes a single file.
    
    Returns "ok" on success.
    """

    workdir: str
    name: str

    def __init__(self, workdir: str, name="file_remove"):
        self.workdir = workdir
        self.name = name


    def __call__(self, filename: str) -> str:
        try:
            resolved_filename = resolve(self.workdir, filename)
        except Exception:
            return "error: invalid filename"

        if not os.path.exists(resolved_filename):
            return "ok"
        
        if not os.path.isfile(resolved_filename):
            return "error: not a file"

        try:
            os.remove(resolved_filename)
        except Exception:
            return "error: failed to remove file"

        return "ok"