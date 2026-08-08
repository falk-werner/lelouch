from lelouch.tools import RemoveFileTool
import os
import tempfile

def test_name():
    """Tool.__name__ should default to `file_remove`."""
    tool = RemoveFileTool("dummy")
    assert "file_remove" == tool.__name__

def test_custom_name():
    """Tool.__name__ can be customized."""
    tool = RemoveFileTool("dummy", name = "custom_name")
    assert "custom_name" == tool.__name__

def test_doc():
    """Tool should have some documentation."""
    tool = RemoveFileTool("dummy")
    assert len(tool.__doc__) > 0

def test_remove_existing_file():
    """Tool should remove an existing regular file."""
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        full_filename = os.path.join(workdir, filename) 
        with open(full_filename, "w", encoding="utf-8") as f:
            f.write("test file")
        assert os.path.isfile(full_filename)

        tool = RemoveFileTool(workdir)
        result = tool(filename)
        assert "ok" == result
        assert not os.path.exists(full_filename)

def test_remove_nonexisting_file_succeeds():
    """
    Tool should succeed when the file is not existing.

    This is because the poscondition (the file is removed)
    is already fulfilled for non-existing files.
    """
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"

        tool = RemoveFileTool(workdir)
        result = tool(filename)
        assert "ok" == result

def test_detect_path_traversal():
    """Tool should report an error, if path traversal is detected."""
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as base_dir:
        workdir = os.path.join(base_dir, "workdir")
        os.mkdir(workdir)

        tool = RemoveFileTool(workdir)
        result = tool("../some_file.txt")
        assert "error: invalid filename" == result

def test_fail_to_remove_directory():
    """
    Tool should report an error, if filename exists, but is not a file.
    
    In this case, the object identified by `filename` should not be removed.
    """
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "some_drectory"
        full_path = os.path.join(workdir, filename)
        os.mkdir(full_path)

        tool = RemoveFileTool(workdir)
        result = tool(filename)
        assert "error: not a file" == result
        assert os.path.exists(full_path)




