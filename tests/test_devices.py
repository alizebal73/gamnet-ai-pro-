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


def test_expired_session_lease_is_paused_on_reconnect(client, admin_client):
    register_device()
    customer = client.post(
        "/api/v1/customers", json={"name": "Lease Customer", "pin": "1234"}
    ).json()
    grant = admin_client.post(
        f"/api/v1/customers/{customer['id']}/credit",
        json={
            "credit_type": "PAID", "seconds": 60, "source": "LEASE-TEST",
            "request_id": "GRANT-LEASE-TEST",
        },
    )
    assert grant.status_code == 201
    client.post(
        "/api/v1/devices/PC-HEARTBEAT-01/heartbeat",
        headers={"X-Device-Token": "device-secret"},
        json={"agent_version": "2.4.1", "pc_state": "READY"},
    )
    session = admin_client.post(
        "/api/v1/sessions",
        json={
            "customer_id": customer["id"], "pc_id": "PC-HEARTBEAT-01",
            "request_id": "SESSION-LEASE-TEST",
        },
    ).json()
    with get_connection() as conn:
        conn.execute(
            "UPDATE sessions SET lease_expires_at = '2020-01-01T00:00:00Z' WHERE id = ?",
            (session["id"],),
        )

    heartbeat = client.post(
        f"/api/v1/devices/PC-HEARTBEAT-01/heartbeat",
        headers={"X-Device-Token": "device-secret"},
        json={"agent_version": "2.4.1", "session_id": session["id"], "pc_state": "BUSY"},
    )

    assert heartbeat.status_code == 200
    assert heartbeat.json()["session_status"] == "PAUSED"