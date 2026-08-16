from lelouch import Agent
from openai import OpenAI
from pytest_httpserver import HTTPServer
from typing import List

class FakeUserInterfaction:
    messages: List[str]
    infos: List[str]
    reasonings: List[str]
    warnings: List[str]

    def __init__(self):
        self.messages = []
        self.infos = []
        self.reasonings = []
        self.warnings = []

    def print(self, message: str):
        self.messages.append(message)

    def info(self, message: str):
        self.infos.append(message)

    def reason(self, message: str):
        self.reasonings.append(message)

    def warn(self, message: str):
        self.warnings.append(message)

    def ask(self, message: str) -> str:
        return "Y"

def test_simple_prompt(httpserver: HTTPServer):
    answer = "I'm a dummy model."
    httpserver.expect_request("/v1/responses").respond_with_json(
        {
            "object": "response",
            "output": [{
                "id": "msg_dummy",
                "type": "message",
                "status": "completed",
                "content": [{
                    "text": answer
                }],     
            }],
        }
    )

    url = httpserver.url_for("/v1")
    client = OpenAI(base_url=url, api_key="empty")
    user_interaction = FakeUserInterfaction()
    agent = Agent(client=client, model="dummy", user_interaction=user_interaction)
    agent.execute("Who are you?")
    assert 1 == len(user_interaction.messages)
    assert "I'm a dummy model." == user_interaction.messages[0]
    assert 0 == len(user_interaction.reasonings)

def test_simple_prompt_with_reasoning(httpserver: HTTPServer):
    reasoning = "Am I a teapot?"
    answer = "I'm a dummy model."
    httpserver.expect_request("/v1/responses").respond_with_json(
        {
            "object": "response",
            "output": [{
                "id": "msg_reason",
                "type": "reasoning",
                "content": [{
                    "text": reasoning
                }]
            },{
                "id": "msg_dummy",
                "type": "message",
                "status": "completed",
                "content": [{
                    "text": answer
                }],     
            }],
        }
    )

    url = httpserver.url_for("/v1")
    client = OpenAI(base_url=url, api_key="empty")
    user_interaction = FakeUserInterfaction()
    agent = Agent(client=client, model="dummy", user_interaction=user_interaction)
    agent.execute("Who are you?")
    assert 1 == len(user_interaction.messages)
    assert answer == user_interaction.messages[0]
    assert 1 == len(user_interaction.reasonings)
    assert reasoning == user_interaction.reasonings[0]

def test_tool_usage(httpserver: HTTPServer):
    httpserver.expect_ordered_request("/v1/responses").respond_with_json({
        "object": "response",
        "output": [{
            "type": "function_call",
            "name": "dummy",
            "arguments": "{}",
            "call_id": "id_dummy",
        }]
    })
    answer = "I'm a dummy model."
    httpserver.expect_request("/v1/responses").respond_with_json(
        {
            "object": "response",
            "output": [{
                "id": "msg_dummy",
                "type": "message",
                "status": "completed",
                "content": [{
                    "text": answer
                }],     
            }],
        }
    )
    url = httpserver.url_for("/v1")
    client = OpenAI(base_url=url, api_key="empty")
    user_interaction = FakeUserInterfaction()
    agent = Agent(client=client, model="dummy", user_interaction=user_interaction)
    agent.execute("Who are you?")
    assert 1 == len(user_interaction.messages)
    assert "I'm a dummy model." == user_interaction.messages[0]
    assert 0 == len(user_interaction.reasonings)
    assert 1 == len(user_interaction.warnings)
    assert "unknown tool dummy" == user_interaction.warnings[0]
