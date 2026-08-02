from lelouch import Tools
import pytest

class NopLogger():
    def info(self, message):
        pass

    def warn(self, message):
        pass

def test_tools_empty_by_default():
    tools = Tools()
    assert 0 == len(tools.tools)
    assert 0 == len(tools.docs)

def test_add_dummy_tool():
    def dummy() -> str:
        """Dummy"""
        return "dummy tool"

    tools = Tools()
    tools.add(dummy)

    assert 1 == len(tools.docs)
    assert "function" == tools.docs[0].get("type")
    assert "dummy" == tools.docs[0].get("name")
    assert "Dummy" == tools.docs[0].get("description")

    assert 1 == len(tools.tools)
    assert "dummy" in tools.tools
    dummy_tool = tools.tools.get("dummy")
    assert dummy == dummy_tool

    docs = tools.get()
    assert 1 == len(docs)
    assert "function" == docs[0].get("type")
    assert "dummy" == docs[0].get("name")
    assert "Dummy" == docs[0].get("description")

    log = NopLogger()
    result = tools.invoke("dummy","{}", log)
    assert "dummy tool" == result

    result = tools.invoke("unknown_tool", "{}", log)
    assert "error: unknown tool" == result

def test_add_with_custom_name():
    def dummy() -> str:
        """Dummy"""
        return "dummy tool"

    tools = Tools()
    tools.add(dummy, name="another_dummy")

    assert 1 == len(tools.docs)
    assert "another_dummy" == tools.docs[0].get("name")

    docs = tools.get()
    assert 1 == len(docs)
    assert "another_dummy" == docs[0].get("name")

def test_add_with_arguments():
    def add(a: int, b: int) -> str:
        """Adds two numbers."""
        return str(a + b)

    tools = Tools()
    tools.add(add)

    docs = tools.get()
    assert 1 == len(docs)
    assert "function" == docs[0].get("type")
    assert "add" == docs[0].get("name")
    assert "Adds two numbers." == docs[0].get("description")
    assert "object" == docs[0].get("parameters").get("type")
    assert "integer" == docs[0].get("parameters").get("properties").get("a").get("type")
    assert "integer" == docs[0].get("parameters").get("properties").get("b").get("type")
    assert "a" in docs[0].get("parameters").get("required")
    assert "b" in docs[0].get("parameters").get("required")


def test_add_fails_with_missing_return_type():
    def dummy():
        pass

    tools = Tools()
    with pytest.raises(RuntimeError):
        tools.add(dummy)

def test_add_fails_with_wrong_return_type():
    def dummy() -> int:
        return 42

    tools = Tools()
    with pytest.raises(RuntimeError):
        tools.add(dummy)

def test_add_fails_without_param_type():
    def dummy(a) -> str:
        return ""

    tools = Tools()
    with pytest.raises(RuntimeError):
        tools.add(dummy)

def test_add_fails_with_unsupported_param_type():
    def dummy(a: str | None) -> str:
        return ""

    tools = Tools()
    with pytest.raises(RuntimeError):
        tools.add(dummy)

def test_invoke_tools_with_arguments():
    def add(a: int, b: int) -> str:
        return str(a + b)

    tools = Tools([add])
    log = NopLogger()
    result = tools.invoke("add", "{\"a\": 1, \"b\": 1}", log)
    assert "2" == result