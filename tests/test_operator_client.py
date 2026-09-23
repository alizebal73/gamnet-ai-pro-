import httpx
import pytest

from gamenet.operator_app.api_client import OperatorApiClient


def test_operator_api_client_authenticates_and_forwards_requests():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/auth/login"):
            return httpx.Response(200, json={"access_token": "operator-token", "user": {"username": "ali"}}, request=request)
        if request.url.path.endswith("/customers/search"):
            return httpx.Response(200, json={"items": [{"id": "CUST-1"}]}, request=request)
        return httpx.Response(500, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    operator = OperatorApiClient("http://server", http_client=client)

    assert operator.login("ali", "password")["username"] == "ali"
    assert operator.search_customers("Ali")[0]["id"] == "CUST-1"
    assert requests[1].headers["Authorization"] == "Bearer operator-token"
    client.close()


def test_operator_api_client_requires_login():
    operator = OperatorApiClient("http://server", http_client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200))))

    with pytest.raises(RuntimeError):
        operator.search_customers("Ali")

    operator.close()