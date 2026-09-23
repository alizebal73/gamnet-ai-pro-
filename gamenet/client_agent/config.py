import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ClientConfig:
    server_url: str
    pc_id: str
    device_token: str
    agent_version: str

    @classmethod
    def from_environment(cls) -> "ClientConfig":
        server_url = os.environ.get("GAMENET_SERVER_URL", "http://127.0.0.1:8765")
        pc_id = os.environ.get("GAMENET_DEVICE_ID", "")
        device_token = os.environ.get("GAMENET_DEVICE_TOKEN", "")
        agent_version = os.environ.get("GAMENET_AGENT_VERSION", "2.4.1")
        if not pc_id or not device_token:
            raise RuntimeError("GAMENET_DEVICE_ID and GAMENET_DEVICE_TOKEN are required")
        return cls(server_url, pc_id, device_token, agent_version)