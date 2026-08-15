from lelouch.tools import RemoveDirectoryTool
import os
import tempfile

def test_name():
    """Tool.__name__ should default to `remove_file`."""
    tool = RemoveDirectoryTool("dummy")
    assert "remove_directory" == tool.__name__

def test_custom_name():
    """Tool.__name__ can be customized."""
    tool = RemoveDirectoryTool("dummy", name = "custom_name")
    assert "custom_name" == tool.__name__

def test_doc():
    """Tool should have some documentation."""
    tool = RemoveDirectoryTool("dummy")
    assert len(tool.__doc__) > 0

def test_remove_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        dirname = "some_directory"
        os.makedirs(os.path.join(workdir, dirname))

        tool = RemoveDirectoryTool(workdir)
        result = tool(dirname)
        assert "ok" == result
        assert not os.path.exists(os.path.join(workdir, dirname))

def test_remove_files_and_subdirectories():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        dirname = "some_directory"
        os.makedirs(os.path.join(workdir, dirname))
        os.makedirs(os.path.join(workdir, dirname, "subdir"))
        with open(os.path.join(workdir, dirname, "test.txt"), "w", encoding="utf-8"):
            pass

        tool = RemoveDirectoryTool(workdir)
        result = tool(dirname)
        assert "ok" == result
        assert not os.path.exists(os.path.join(workdir, dirname))

def test_do_not_remove_parent_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        parent = "parent"
        dirname = "some_directory"
        os.makedirs(os.path.join(workdir, parent, dirname))

        tool = RemoveDirectoryTool(workdir)
        result = tool(os.path.join(parent, dirname))
        assert "ok" == result
        assert not os.path.exists(os.path.join(workdir, parent, dirname))
        assert os.path.isdir(os.path.join(workdir, parent))

def test_fail_to_remove_file():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        with open(os.path.join(workdir, filename), "w", encoding="utf-8"):
            pass

        tool = RemoveDirectoryTool(workdir)
        result = tool(filename)
        assert "error: not a directory" == result
        assert os.path.exists(os.path.join(workdir, filename))

def test_fail_to_remove_nonexisting_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        dirname = "some_directory"

        tool = RemoveDirectoryTool(workdir)
        result = tool(dirname)
        assert "error: not a directory" == result

def test_fail_to_remove_ignored_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        dirname = ".hidden"
        os.makedirs(os.path.join(workdir, dirname))

        tool = RemoveDirectoryTool(workdir)
        result = tool(dirname)
        assert "error: not a directory" == result
