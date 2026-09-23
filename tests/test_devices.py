from gamenet.server.db import get_connection
from gamenet.server.security.passwords import hash_secret


def register_device():
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO pcs
                (id, device_code, display_name, status, created_at, updated_at)
            VALUES ('PC-HEARTBEAT-01', 'PC-HEARTBEAT-01', 'Heartbeat PC', 'OFFLINE',
                    '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
            """
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO device_credentials (pc_id, secret_hash, created_at)
            VALUES ('PC-HEARTBEAT-01', ?, '2026-01-01T00:00:00Z')
            """,
            (hash_secret("device-secret"),),
        )


def test_device_heartbeat_updates_health_and_rejects_invalid_token(client):
    register_device()
    payload = {"agent_version": "2.4.1", "pc_state": "READY"}

    invalid = client.post(
        "/api/v1/devices/PC-HEARTBEAT-01/heartbeat",
        headers={"X-Device-Token": "wrong-secret"},
        json=payload,
    )
    assert invalid.status_code == 401

    valid = client.post(
        "/api/v1/devices/PC-HEARTBEAT-01/heartbeat",
        headers={"X-Device-Token": "device-secret"},
        json=payload,
    )
    assert valid.status_code == 200
    assert valid.json()["pc_status"] == "READY"
    assert valid.json()["session_id"] is None

    with get_connection() as conn:
        pc = conn.execute("SELECT status, agent_version, last_seen_at FROM pcs WHERE id = ?", ("PC-HEARTBEAT-01",)).fetchone()
    assert pc["status"] == "READY"
    assert pc["agent_version"] == "2.4.1"
    assert pc["last_seen_at"]