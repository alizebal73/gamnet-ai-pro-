import pytest

from gamenet.client_agent.config import ClientConfig


def test_client_config_requires_device_identity(monkeypatch):
    monkeypatch.delenv("GAMENET_DEVICE_ID", raising=False)
    monkeypatch.delenv("GAMENET_DEVICE_TOKEN", raising=False)

    with pytest.raises(RuntimeError):
        ClientConfig.from_environment()


def test_client_config_reads_environment(monkeypatch):
    monkeypatch.setenv("GAMENET_SERVER_URL", "http://server:8765")
    monkeypatch.setenv("GAMENET_DEVICE_ID", "PC-01")
    monkeypatch.setenv("GAMENET_DEVICE_TOKEN", "secret")
    monkeypatch.setenv("GAMENET_AGENT_VERSION", "3.0.0")

    config = ClientConfig.from_environment()

    assert config.server_url == "http://server:8765"
    assert config.pc_id == "PC-01"
    assert config.agent_version == "3.0.0"