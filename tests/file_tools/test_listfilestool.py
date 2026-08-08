from lelouch.tools import ListFilesTool
import os
import tempfile
import json

def file_write(filename: str, content: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def test_name():
    tool = ListFilesTool("dummy")
    assert "list_files" == tool.__name__

def test_custom_name():
    tool = ListFilesTool("dummy", name = "custom_name")
    assert "custom_name" == tool.__name__

def test_doc():
    tool = ListFilesTool("dummy")
    assert len(tool.__doc__) > 0

def test_list_files():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filenames = ["a.txt", "b.txt", "c.txt"]
        for filename in filenames:
            file_write(os.path.join(workdir, filename), f"test file {filename}")

        tool = ListFilesTool(workdir)
        result = json.loads(tool())

        assert len(result) == len(filenames)
        for filename in filenames:
            assert filename in result

def test_list_files_including_nested_directories():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filenames = ["a/test.txt", "b/test.txt", "c/test.txt"]
        for filename in filenames:
            full_filename = os.path.join(workdir, filename)
            dirname = os.path.dirname(full_filename)
            os.makedirs(dirname, exist_ok=True) 
            file_write(full_filename, f"test file {filename}")

        tool = ListFilesTool(workdir)
        result = json.loads(tool())

        assert len(result) == len(filenames)
        for filename in filenames:
            assert filename in result

def test_do_not_list_directories_and_links():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        os.makedirs(os.path.join(workdir, "a"))
        file_write(os.path.join(workdir,"foo.txt"), "test file")
        os.symlink(os.path.join(workdir,"foo.txt"), os.path.join(workdir,"bar.txt"))

        tool = ListFilesTool(workdir)
        result = json.loads(tool())

        assert len(result) == 1
        assert result[0] == "foo.txt"
    
def test_do_not_list_hidden_files_and_directories():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filenames = [".hidden", ".a/.also_hidden.txt", ".b/another_hidden.txt", "c/a/.hidden.txt"]
        for filename in filenames:
            full_filename = os.path.join(workdir, filename)
            dirname = os.path.dirname(full_filename)
            os.makedirs(dirname, exist_ok=True) 
            file_write(full_filename, f"test file {filename}")

        tool = ListFilesTool(workdir)
        result = json.loads(tool())

        assert len(result) == 0
        
