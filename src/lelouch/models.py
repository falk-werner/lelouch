
from openai import OpenAI

def list_models(client: OpenAI | None = None):
    client = client if client else OpenAI()
    models = client.models.list()
    result = []
    for item in models.data:
        if item.object == "model":
            result.append(item.id)
    return result
