from gamenet.server.db import get_connection
from gamenet.server.security.passwords import hash_secret


def test_device_websocket_auth_and_heartbeat(client):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO pcs (id, device_code, display_name, status, created_at, updated_at) VALUES ('PC-WS-01', 'PC-WS-01', 'WebSocket PC', 'OFFLINE', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO device_credentials (pc_id, secret_hash, created_at) VALUES ('PC-WS-01', ?, '2026-01-01T00:00:00Z')",
            (hash_secret("ws-secret"),),
        )

    with client.websocket_connect("/api/v1/ws/devices/PC-WS-01") as websocket:
        websocket.send_json({"message_type": "AUTH", "device_token": "ws-secret"})
        assert websocket.receive_json()["message_type"] == "AUTH_ACK"
        websocket.send_json({
            "message_type": "HEARTBEAT", "request_id": "WS-HB-1",
            "payload": {"agent_version": "2.4.1", "pc_state": "READY"},
        })
        response = websocket.receive_json()
        assert response["message_type"] == "HEARTBEAT_ACK"
        assert response["request_id"] == "WS-HB-1"
        assert response["payload"]["pc_status"] == "READY"