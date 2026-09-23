import uuid

from gamenet.server.db import get_connection, utc_now_iso


def test_shift_open_close_reconciles_cash(client):
    opened = client.post(
        "/api/v1/shifts", json={"opening_cash": 10000, "request_id": "SHIFT-OPEN-1"}
    )
    assert opened.status_code == 201
    shift = opened.json()
    duplicate = client.post(
        "/api/v1/shifts", json={"opening_cash": 99999, "request_id": "SHIFT-OPEN-2"}
    )
    assert duplicate.json()["id"] == shift["id"]

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO cash_movements (id, shift_id, delta_amount, event_type, request_id, reason, created_at) VALUES (?, ?, ?, 'SALE', ?, ?, ?)",
            (f"CASH-{uuid.uuid4().hex[:12].upper()}", shift["id"], 5000, "SHIFT-CASH-1", "Test sale", utc_now_iso()),
        )

    closed = client.post(
        f"/api/v1/shifts/{shift['id']}/close",
        json={"actual_cash": 14000, "reason": "Cash count", "request_id": "SHIFT-CLOSE-1"},
    )
    assert closed.status_code == 200
    assert closed.json()["expected_cash"] == 15000
    assert closed.json()["difference"] == -1000