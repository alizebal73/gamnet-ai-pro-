import json

import httpx

from gamenet.client_agent.agent import AgentConfig, ClientAgent


def test_agent_heartbeat_and_connection_loss_state():
    requests = []
    should_fail = False

    def handler(request: httpx.Request) -> httpx.Response:
        if should_fail:
            raise httpx.ConnectError("server unavailable", request=request)
        requests.append(request)
        return httpx.Response(
            200,
            json={"session_status": "ACTIVE", "server_time": "2026-09-23T00:00:00Z"},
            request=request,
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    states = []
    agent = ClientAgent(
        AgentConfig("http://server", "PC-01", "secret", "2.4.1"),
        http_client=client,
        on_state_change=states.append,
    )
    agent.set_session("SESSION-1")

    response = agent.heartbeat()

    assert response["session_status"] == "ACTIVE"
    assert agent.state == "CONNECTED"
    assert requests[0].headers["X-Device-Token"] == "secret"
    assert json.loads(requests[0].content)["session_id"] == "SESSION-1"

    should_fail = True
    disconnected = agent.heartbeat()
    assert disconnected["session_status"] == "PAUSED_BY_CONNECTION"
    assert agent.state == "PAUSED_BY_CONNECTION"
    assert states == ["CONNECTED", "PAUSED_BY_CONNECTION"]
    client.close()


def test_agent_does_not_auto_resume_after_connection_recovery():
    responses = iter([
        {"session_status": "ACTIVE", "server_time": "2026-09-23T00:00:00Z"},
        {"session_status": "ACTIVE", "server_time": "2026-09-23T00:00:02Z"},
    ])

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=next(responses), request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    agent = ClientAgent(AgentConfig("http://server", "PC-01", "secret", "2.4.1"), http_client=client)
    agent.set_session("SESSION-1")
    agent.heartbeat()
    agent.state = "PAUSED_BY_CONNECTION"

    agent.heartbeat()

    assert agent.state == "PAUSED"
    client.close()