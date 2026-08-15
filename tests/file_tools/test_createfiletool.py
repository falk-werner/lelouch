from lelouch.tools import CreateFileTool
import os
import tempfile

def write_test_file(filename: str, content: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def read_test_file(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def test_name():
    tool = CreateFileTool("dummy")
    assert "create_file" == tool.__name__

def test_custom_name():
    tool = CreateFileTool("dummy", name="custom_name")
    assert "custom_name" == tool.__name__

def test_doc():
    tool = CreateFileTool("dummy")
    assert len(tool.__doc__) > 0

def test_create_file():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"

        tool = CreateFileTool(workdir)
        result = tool(filename, "test")
        assert result == "ok"

        content = read_test_file(os.path.join(workdir, filename))
        assert content == "test"

def test_create_parent_directories():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "some/nested/path/test.txt"

        tool = CreateFileTool(workdir)
        result = tool(filename, "test")
        assert result == "ok"

        content = read_test_file(os.path.join(workdir, filename))
        assert content == "test"


def test_overwrite_existing_file():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename), "old")

        tool = CreateFileTool(workdir)
        result = tool(filename, "test")
        assert result == "ok"

        content = read_test_file(os.path.join(workdir, filename))
        assert content == "test"

def test_edit_fails_file_ignored():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"

        tool = CreateFileTool(workdir, ignored_files=["test.txt"])
        result = tool(filename, "text")
        assert result == "error: failed to create file"

def test_edit_fails_file_is_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "some_directory"
        os.makedirs(os.path.join(workdir, filename))

        tool = CreateFileTool(workdir)
        result = tool(filename, "test")
        assert result == "error: failed to create file"

def test_edit_fails_file_is_not_writable():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename), "old")
        os.chmod(os.path.join(workdir, filename), 0o444)

        tool = CreateFileTool(workdir)
        result = tool(filename, "test")
        assert result == "error: failed to create file"

