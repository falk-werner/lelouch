from lelouch.tools import EditFileTool
import os
import tempfile

def write_test_file(filename: str, content: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def read_test_file(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def test_name():
    tool = EditFileTool("dummy")
    assert "edit_file" == tool.__name__

def test_custom_name():
    tool = EditFileTool("dummy", name="custom_name")
    assert "custom_name" == tool.__name__

def test_doc():
    tool = EditFileTool("dummy")
    assert len(tool.__doc__) > 0

def test_edit_file():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename), "old")

        tool = EditFileTool(workdir)
        result = tool(filename, "old", "new")
        assert result == "ok"

        content = read_test_file(os.path.join(workdir, filename))
        assert content == "new"

def test_edit_fails_old_not_found():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename), "old")

        tool = EditFileTool(workdir)
        result = tool(filename, "invalid", "new")
        assert result == "error: cannot find `old` in file"

def test_edit_fails_old_not_unique():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename), "old older oldest")

        tool = EditFileTool(workdir)
        result = tool(filename, "old", "new")
        assert result == "error: found `old` muliple times in file; please add more context"

def test_edit_fails_file_not_found():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"

        tool = EditFileTool(workdir)
        result = tool(filename, "old", "new")
        assert result == "error: file not found"

def test_edit_fails_file_ignored():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename), "old")

        tool = EditFileTool(workdir, ignored_files=["test.txt"])
        result = tool(filename, "old", "new")
        assert result == "error: file not found"

def test_edit_fails_file_is_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "some_directory"
        os.makedirs(os.path.join(workdir, filename))

        tool = EditFileTool(workdir)
        result = tool(filename, "old", "new")
        assert result == "error: failed to read file"

def test_edit_fails_file_is_not_writable():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename), "old")
        os.chmod(os.path.join(workdir, filename), 0o444)

        tool = EditFileTool(workdir)
        result = tool(filename, "old", "new")
        assert result == "error: failed to write file"
