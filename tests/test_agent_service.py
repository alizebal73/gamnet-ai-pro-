import threading

import pytest

from gamenet.client_agent.agent import AgentConfig
from gamenet.client_agent.service import AgentRuntime, run_windows_service


def test_agent_runtime_stop_is_independent_from_ui():
    runtime = AgentRuntime(AgentConfig("http://server", "PC-01", "secret", "2.4.1"))
    assert not runtime.stop_event.is_set()
    runtime.stop()
    assert runtime.stop_event.is_set()


def test_windows_service_wrapper_is_platform_guarded():
    if __import__("sys").platform == "win32":
        pytest.skip("Windows service integration requires an installed service host")
    with pytest.raises(RuntimeError, match="Windows"):
        run_windows_service(AgentConfig("http://server", "PC-01", "secret", "2.4.1"))