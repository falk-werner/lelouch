from lelouch import Tools

class NopLogger():
    def info(self, message):
        pass

    def warn(self, message):
        pass


def dummy() -> str:
    """Dummy"""
    return "dummy tool"

def test_tools_empty_by_default():
    tools = Tools()
    assert 0 == len(tools.tools)
    assert 0 == len(tools.docs)

def test_add_dummy_tool():
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
    tools = Tools()
    tools.add(dummy, name="another_dummy")

    assert 1 == len(tools.docs)
    assert "another_dummy" == tools.docs[0].get("name")

    docs = tools.get()
    assert 1 == len(docs)
    assert "another_dummy" == docs[0].get("name")
