from lelouch import list_models
from openai import OpenAI, NotFoundError
import pytest
from pytest_httpserver import HTTPServer

def test_list_models(httpserver: HTTPServer):
    httpserver.expect_request("/v1/models").respond_with_json(
        {"data": [{"object": "model", "id": "foo"}]}
    )

    url = httpserver.url_for("/v1")
    client = OpenAI(base_url=url, api_key="empty")
    models = list_models(client=client)
    assert 1 == len(models)
    assert "foo" == models[0]

def test_list_models_fail_with_missing_data(httpserver: HTTPServer):
    httpserver.expect_request("/v1/models").respond_with_json(
        {}
    )

    url = httpserver.url_for("/v1")
    client = OpenAI(base_url=url, api_key="empty")

    with pytest.raises(TypeError):
        list_models(client=client)

def test_list_models_fail_with_404_not_found(httpserver: HTTPServer):
    httpserver.expect_request("/v1/models").respond_with_data(
        "Not found",
        status="404",
        content_type="text/plain",
    )

    url = httpserver.url_for("/v1")
    client = OpenAI(base_url=url, api_key="empty")

    with pytest.raises(NotFoundError):
        list_models(client=client)
