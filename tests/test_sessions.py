from gamenet.server.db import get_connection


def register_ready_pc():
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO pcs
                (id, device_code, display_name, status, created_at, updated_at)
            VALUES ('PC-TEST-01', 'PC-TEST-01', 'Test PC', 'READY',
                    '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')
            """
        )


def grant(admin_client, customer_id, request_id, seconds):
    return admin_client.post(
        f"/api/v1/customers/{customer_id}/credit",
        json={
            "credit_type": "PAID",
            "seconds": seconds,
            "source": request_id,
            "request_id": request_id,
        },
    )


def test_session_consumes_credit_and_preserves_state(client, admin_client):
    register_ready_pc()
    customer = client.post(
        "/api/v1/customers", json={"name": "Session Customer", "pin": "1234"}
    ).json()
    assert grant(admin_client, customer["id"], "GRANT-SESSION-1", 60).status_code == 201
    assert grant(admin_client, customer["id"], "GRANT-SESSION-2", 120).status_code == 201

    payload = {
        "customer_id": customer["id"],
        "pc_id": "PC-TEST-01",
        "request_id": "SESSION-START-1",
    }
    started = admin_client.post("/api/v1/sessions", json=payload)
    duplicate_start = admin_client.post("/api/v1/sessions", json=payload)
    assert started.status_code == 201
    assert duplicate_start.json()["id"] == started.json()["id"]
    session_id = started.json()["id"]

    consume_payload = {"seconds": 90, "request_id": "CONSUME-SESSION-1"}
    consumed = admin_client.post(f"/api/v1/sessions/{session_id}/consume", json=consume_payload)
    duplicate_consume = admin_client.post(f"/api/v1/sessions/{session_id}/consume", json=consume_payload)
    assert consumed.status_code == 200
    assert consumed.json()["consumed_seconds"] == 90
    assert duplicate_consume.json()["consumed_seconds"] == 90

    paused = admin_client.post(
        f"/api/v1/sessions/{session_id}/pause",
        json={"request_id": "PAUSE-SESSION-1", "reason": "Network check"},
    )
    resumed = admin_client.post(
        f"/api/v1/sessions/{session_id}/resume",
        json={"request_id": "RESUME-SESSION-1"},
    )
    ended = admin_client.post(
        f"/api/v1/sessions/{session_id}/end",
        json={"request_id": "END-SESSION-1"},
    )
    assert paused.json()["status"] == "PAUSED"
    assert resumed.json()["status"] == "ACTIVE"
    assert ended.json()["status"] == "ENDED"


def test_one_active_session_per_customer(client, admin_client):
    register_ready_pc()
    customer = client.post(
        "/api/v1/customers", json={"name": "Single Session Customer", "pin": "1234"}
    ).json()
    assert grant(admin_client, customer["id"], "GRANT-SINGLE-1", 60).status_code == 201
    assert admin_client.post(
        "/api/v1/sessions",
        json={"customer_id": customer["id"], "pc_id": "PC-TEST-01", "request_id": "SESSION-SINGLE-1"},
    ).status_code == 201

    response = admin_client.post(
        "/api/v1/sessions",
        json={"customer_id": customer["id"], "pc_id": "PC-TEST-01", "request_id": "SESSION-SINGLE-2"},
    )
    assert response.status_code == 409