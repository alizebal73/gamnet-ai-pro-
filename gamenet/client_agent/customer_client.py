import httpx


class CustomerApiClient:
    def __init__(self, base_url: str, pc_id: str, device_token: str, http_client: httpx.Client | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.pc_id = pc_id
        self.device_token = device_token
        self._client = http_client or httpx.Client(timeout=5.0)
        self._owns_client = http_client is None

    def login(self, customer_number: int, pin: str) -> dict:
        response = self._client.post(
            f"{self.base_url}/api/v1/devices/{self.pc_id}/customer-login",
            headers={"X-Device-Token": self.device_token},
            json={"customer_number": customer_number, "pin": pin},
        )
        response.raise_for_status()
        return response.json()

    def games(self) -> list[dict]:
        response = self._client.get(
            f"{self.base_url}/api/v1/devices/{self.pc_id}/games",
            headers={"X-Device-Token": self.device_token},
        )
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()