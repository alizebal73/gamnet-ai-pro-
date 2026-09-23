from dataclasses import dataclass
from threading import Event
from typing import Callable

import httpx


@dataclass(frozen=True)
class AgentConfig:
    server_url: str
    pc_id: str
    device_token: str
    agent_version: str
    heartbeat_interval_sec: float = 1.0
    request_timeout_sec: float = 2.0


class ClientAgent:
    """Small transport-agnostic Agent core; Windows service/UI wrap this class."""

    def __init__(
        self,
        config: AgentConfig,
        http_client: httpx.Client | None = None,
        on_state_change: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self._client = http_client or httpx.Client(timeout=config.request_timeout_sec)
        self._owns_client = http_client is None
        self._on_state_change = on_state_change
        self.state = "DISCONNECTED"
        self.session_id: str | None = None

    def set_session(self, session_id: str | None) -> None:
        self.session_id = session_id

    def heartbeat(self) -> dict:
        was_connection_paused = self.state == "PAUSED_BY_CONNECTION"
        try:
            response = self._client.post(
                f"{self.config.server_url.rstrip('/')}/api/v1/devices/{self.config.pc_id}/heartbeat",
                headers={"X-Device-Token": self.config.device_token},
                json={
                    "agent_version": self.config.agent_version,
                    "session_id": self.session_id,
                    "pc_state": "BUSY" if self.session_id else "READY",
                },
            )
            response.raise_for_status()
            body = response.json()
            if body.get("session_status") == "PAUSED" or (
                was_connection_paused and body.get("session_status") == "ACTIVE"
            ):
                self._set_state("PAUSED")
            else:
                self._set_state("CONNECTED")
            return body
        except (httpx.HTTPError, ValueError):
            self._set_state("PAUSED_BY_CONNECTION")
            return {"session_status": "PAUSED_BY_CONNECTION"}

    def run(self, stop_event: Event) -> None:
        while not stop_event.is_set():
            self.heartbeat()
            stop_event.wait(self.config.heartbeat_interval_sec)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _set_state(self, state: str) -> None:
        if self.state == state:
            return
        self.state = state
        if self._on_state_change:
            self._on_state_change(state)