from gamenet.server.db import get_connection


def test_sensitive_operations_write_audit_once(client, admin_client):
    customer = client.post(
        "/api/v1/customers", json={"name": "Audit Customer", "pin": "1234"}
    ).json()
    credit_payload = {
        "credit_type": "BONUS", "seconds": 300, "source": "AUDIT-TEST",
        "request_id": "AUDIT-GRANT-1", "reason": "Test grant",
    }
    first_grant = admin_client.post(
        f"/api/v1/customers/{customer['id']}/credit", json=credit_payload
    )
    duplicate_grant = admin_client.post(
        f"/api/v1/customers/{customer['id']}/credit", json=credit_payload
    )
    assert first_grant.status_code == 201
    assert duplicate_grant.status_code == 201

    sale = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "FOOD", "item_name": "Audit Snack",
            "duration_seconds": 0, "amount": 1000, "payment_method": "CASH",
            "request_id": "AUDIT-SALE-1",
        },
    ).json()
    confirmed = client.post(
        f"/api/v1/sales/{sale['id']}/confirm",
        json={"reference": "AUDIT-CASH", "request_id": "AUDIT-PAYMENT-1"},
    )
    assert confirmed.status_code == 200

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT action, request_id, user_id FROM audit_logs WHERE request_id IN (?, ?, ?) ORDER BY action",
            ("AUDIT-GRANT-1", "AUDIT-SALE-1", "AUDIT-PAYMENT-1"),
        ).fetchall()

    assert [row["action"] for row in rows] == [
        "CREDIT_GRANTED", "PAYMENT_CONFIRMED", "SALE_CREATED"
    ]
    assert sum(row["request_id"] == "AUDIT-GRANT-1" for row in rows) == 1
    assert all(row["user_id"] for row in rows)