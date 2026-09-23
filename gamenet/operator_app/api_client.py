from dataclasses import dataclass

import httpx


@dataclass
class OperatorApiClient:
    base_url: str
    http_client: httpx.Client | None = None

    def __post_init__(self) -> None:
        self._client = self.http_client or httpx.Client(timeout=5.0)
        self._owns_client = self.http_client is None
        self._token: str | None = None

    def login(self, username: str, password: str) -> dict:
        response = self._client.post(
            f"{self.base_url.rstrip('/')}/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        body = response.json()
        self._token = body["access_token"]
        return body["user"]

    def search_customers(self, query: str) -> list[dict]:
        return self._request("GET", "/api/v1/customers/search", params={"q": query})["items"]

    def quote(self, item_type: str, duration_seconds: int) -> dict:
        return self._request(
            "POST", "/api/v1/pricing/quote",
            json={"item_type": item_type, "duration_seconds": duration_seconds},
        )

    def create_sale(self, payload: dict) -> dict:
        return self._request("POST", "/api/v1/sales", json=payload)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _request(self, method: str, path: str, **kwargs) -> dict:
        if not self._token:
            raise RuntimeError("Operator must login before making API requests")
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._token}"
        response = self._client.request(
            method, f"{self.base_url.rstrip('/')}{path}", headers=headers, **kwargs
        )
        response.raise_for_status()
        return response.json()