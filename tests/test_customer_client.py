import httpx

from gamenet.client_agent.customer_client import CustomerApiClient


def test_customer_client_uses_device_authentication():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Device-Token"] == "device-secret"
        if request.method == "POST":
            return httpx.Response(200, json={"customer_id": "CUST-1"}, request=request)
        return httpx.Response(200, json=[], request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    customer_client = CustomerApiClient("http://server", "PC-01", "device-secret", client)
    assert customer_client.login(1040, "1234")["customer_id"] == "CUST-1"
    assert customer_client.games() == []
    client.close()