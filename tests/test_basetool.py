from lelouch.tools import BaseTool

def test_name_property():
    class MyTool(BaseTool):
        def __init__(self):
            super(MyTool, self).__init__("my_tool")

    my_tool = MyTool()
    assert "my_tool" == my_tool.name
