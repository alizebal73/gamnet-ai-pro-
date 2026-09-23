from gamenet.server.db import get_connection


def test_reservation_conflict_is_rejected(client):
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO pcs (id, device_code, display_name, status, created_at, updated_at) VALUES ('PC-RES-01', 'PC-RES-01', 'Reservation PC', 'READY', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')")
    customer = client.post(
        "/api/v1/customers", json={"name": "Reservation Customer", "pin": "1234"}
    ).json()
    payload = {
        "customer_id": customer["id"], "pc_id": "PC-RES-01",
        "starts_at": "2026-10-01T10:00:00Z", "ends_at": "2026-10-01T12:00:00Z",
        "request_id": "RES-TEST-1",
    }
    first = client.post("/api/v1/reservations", json=payload)
    assert first.status_code == 201
    duplicate = client.post("/api/v1/reservations", json=payload)
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == first.json()["id"]
    conflict = client.post(
        "/api/v1/reservations",
        json={**payload, "ends_at": "2026-10-01T11:00:00Z", "request_id": "RES-TEST-2"},
    )
    assert conflict.status_code == 409