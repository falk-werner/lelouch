from lelouch.tools import ReadFileTool
import os
import tempfile
import json

def write_test_file(filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("first\nsecond\nthird\n4th\n5th\n")

def test_name():
    tool = ReadFileTool("dummy")
    assert "read_file" == tool.__name__

def test_custom_name():
    tool = ReadFileTool("dummy", name="custom_name")
    assert "custom_name" == tool.__name__

def test_doc():
    tool = ReadFileTool("dummy")
    assert len(tool.__doc__) > 0

def test_read_full_file():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename))

        tool = ReadFileTool(workdir)
        result = json.loads(tool(filename))
        assert result.get("first_line") == 0
        assert result.get("total_lines") == 5
        lines = result.get("lines")
        assert len(lines) == 5
        assert "first\n" == lines[0]
        assert "second\n" == lines[1]
        assert "third\n" == lines[2]
        assert "4th\n" == lines[3]
        assert "5th\n" == lines[4]

def test_read_range():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename))

        tool = ReadFileTool(workdir)
        result = json.loads(tool(filename, first_line=1, line_count=3))
        assert result.get("first_line") == 1
        assert result.get("total_lines") == 5
        lines = result.get("lines")
        assert len(lines) == 3
        assert "second\n" == lines[0]
        assert "third\n" == lines[1]
        assert "4th\n" == lines[2]

def test_read_from_given_line_to_end():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename))

        tool = ReadFileTool(workdir)
        result = json.loads(tool(filename, first_line=3))
        assert result.get("first_line") == 3
        assert result.get("total_lines") == 5
        lines = result.get("lines")
        assert len(lines) == 2
        assert "4th\n" == lines[0]
        assert "5th\n" == lines[1]

def test_read_after_end():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename))

        tool = ReadFileTool(workdir)
        result = json.loads(tool(filename, first_line=10))
        assert result.get("first_line") == 10
        assert result.get("total_lines") == 5
        lines = result.get("lines")
        assert len(lines) == 0

def test_read_less_lines_than_requested():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename))

        tool = ReadFileTool(workdir)
        result = json.loads(tool(filename, first_line=2, line_count=10))
        assert result.get("first_line") == 2
        assert result.get("total_lines") == 5
        lines = result.get("lines")
        assert len(lines) == 3
        assert "third\n" == lines[0]
        assert "4th\n" == lines[1]
        assert "5th\n" == lines[2]

def test_fail_to_read_with_negative_start():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.txt"
        write_test_file(os.path.join(workdir, filename))

        tool = ReadFileTool(workdir)
        result = json.loads(tool(filename, first_line=-1))
        assert result.get("error") == "invalid arguments"

def test_fail_with_wrong_filename_type():
    tool = ReadFileTool("dummy")
    result = json.loads(tool(None))
    assert result.get("error") == "invalid arguments"

def test_fail_with_wrong_first_line_type():
    tool = ReadFileTool("dummy")
    result = json.loads(tool("test.txt", first_line=None))
    assert result.get("error") == "invalid arguments"

def test_fail_with_wrong_line_count_type():
    tool = ReadFileTool("dummy")
    result = json.loads(tool("test.txt", line_count=None))
    assert result.get("error") == "invalid arguments"

def test_fail_to_read_nonexisting_file():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        tool = ReadFileTool(workdir)
        result = json.loads(tool("test.txt"))
        assert result.get("error") == "file not found"

def test_fail_to_read_ignored_file():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = ".hidden"
        write_test_file(os.path.join(workdir, filename))

        tool = ReadFileTool(workdir)
        result = json.loads(tool(filename))
        assert result.get("error") == "file not found"

def test_fail_to_read_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "dir"
        os.makedirs(os.path.join(workdir, filename))

        tool = ReadFileTool(workdir)
        result = json.loads(tool(filename))
        assert result.get("error") == "not a file"

def test_fail_to_read_out_of_directory():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as basedir:
        workdir = os.path.join(basedir, "workdir")
        os.makedirs(workdir)
        filename = "../text.txt"
        write_test_file(os.path.join(workdir, filename))

        tool = ReadFileTool(workdir)
        result = json.loads(tool(filename))
        assert result.get("error") == "invalid filename"

def test_fail_to_read_binary_file():
    with tempfile.TemporaryDirectory(prefix="lelouch_test_", delete=True) as workdir:
        filename = "test.bin"
        with open(os.path.join(workdir, filename), "wb") as f:
            f.write(b'\xff')

        tool = ReadFileTool(workdir)
        result = json.loads(tool(filename))
        assert result.get("error") == "failed to read file"
