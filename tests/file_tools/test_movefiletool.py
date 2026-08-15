from lelouch.tools import MoveFileTool
import os
import tempfile

def write_test_file(filename: str, content: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def read_test_file(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def test_name():
    tool = MoveFileTool("dummy")
    assert "move_file" == tool.__name__

def test_custom_name():
    tool = MoveFileTool("dummy", name="custom_name")
    assert "custom_name" == tool.__name__

def test_doc():
    tool = MoveFileTool("dummy")
    assert len(tool.__doc__) > 0

def test_move_file():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        old_filename = "old.txt"
        new_filename = "new.txt"
        write_test_file(os.path.join(workdir, old_filename), "test")

        tool = MoveFileTool(workdir)
        result = tool(old_filename, new_filename)
        assert result == "ok"

        assert not os.path.exists(os.path.join(workdir, old_filename))
        assert os.path.isfile(os.path.join(workdir, new_filename))
        assert "test" == read_test_file(os.path.join(workdir, new_filename))

def test_move_creates_parent_directories():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        old_filename = "old.txt"
        new_filename = "some/nested/path/new.txt"
        write_test_file(os.path.join(workdir, old_filename), "test")

        tool = MoveFileTool(workdir)
        result = tool(old_filename, new_filename)
        assert result == "ok"

        assert not os.path.exists(os.path.join(workdir, old_filename))
        assert os.path.isfile(os.path.join(workdir, new_filename))
        assert "test" == read_test_file(os.path.join(workdir, new_filename))

def test_move_fails_file_not_found():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        old_filename = "old.txt"
        new_filename = "new.txt"

        tool = MoveFileTool(workdir)
        result = tool(old_filename, new_filename)
        assert result == "error: file not found"

def test_move_fails_file_ignored():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        old_filename = "old.txt"
        new_filename = "new.txt"
        write_test_file(os.path.join(workdir, old_filename), "test")

        tool = MoveFileTool(workdir, ignored_files=["old.txt"])
        result = tool(old_filename, new_filename)
        assert result == "error: file not found"

def test_move_fails_target_exists():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        old_filename = "old.txt"
        new_filename = "new.txt"
        write_test_file(os.path.join(workdir, old_filename), "test")
        write_test_file(os.path.join(workdir, new_filename), "new")

        tool = MoveFileTool(workdir)
        result = tool(old_filename, new_filename)
        assert result == "error: new_filename already exists"

        assert os.path.exists(os.path.join(workdir, old_filename))
        assert "test" == read_test_file(os.path.join(workdir, old_filename))
        assert os.path.isfile(os.path.join(workdir, new_filename))
        assert "new" == read_test_file(os.path.join(workdir, new_filename))

def test_move_fails_target_is_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        old_filename = "old.txt"
        new_filename = "some_directory"
        write_test_file(os.path.join(workdir, old_filename), "test")
        os.makedirs(os.path.join(workdir, new_filename))

        tool = MoveFileTool(workdir)
        result = tool(old_filename, new_filename)
        assert result == "error: new_filename already exists"

        assert os.path.exists(os.path.join(workdir, old_filename))
        assert "test" == read_test_file(os.path.join(workdir, old_filename))
        assert os.path.isdir(os.path.join(workdir, new_filename))
