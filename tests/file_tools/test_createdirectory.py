from lelouch.tools import CreateDirectoryTool
import os
import tempfile

def test_name():
    tool = CreateDirectoryTool("dummy")
    assert "create_directory" == tool.__name__

def test_custom_name():
    tool = CreateDirectoryTool("dummy", name="custom_name")
    assert "custom_name" == tool.__name__

def test_doc():
    tool = CreateDirectoryTool("dummy")
    assert len(tool.__doc__) > 0

def test_create_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        dirname = "some_directory"

        tool = CreateDirectoryTool(workdir)
        result = tool(dirname)
        assert result == "ok"

        assert os.path.isdir(os.path.join(workdir, dirname))

def test_create_already_existing_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        dirname = "some_directory"
        os.makedirs(os.path.join(workdir, dirname))

        tool = CreateDirectoryTool(workdir)
        result = tool(dirname)
        assert result == "ok"

        assert os.path.isdir(os.path.join(workdir, dirname))


def test_create_nested_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        dirname = "some/nested/directory"

        tool = CreateDirectoryTool(workdir)
        result = tool(dirname)
        assert result == "ok"

        assert os.path.isdir(os.path.join(workdir, dirname))

def test_fail_path_traversal():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        dirname = "../path_traversal"

        tool = CreateDirectoryTool(workdir)
        result = tool(dirname)
        assert result == "error: invalid dirname"

def test_fail_dirname_is_existing_file():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        dirname = "some_directory"
        with open(os.path.join(workdir, dirname), "w", encoding="utf-8") as f:
            pass

        tool = CreateDirectoryTool(workdir)
        result = tool(dirname)
        assert result == "error: dirname already exists"
