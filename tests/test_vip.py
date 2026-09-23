from gamenet.server.db import get_connection


def test_vip_activates_only_after_payment(client, admin_client):
    plan = admin_client.post(
        "/api/v1/vip/plans",
        json={"name": "VIP One Month", "duration_days": 30, "price": 150000, "discount_percent": 20},
    )
    assert plan.status_code == 201
    plan_id = plan.json()["id"]
    assert any(item["id"] == plan_id for item in client.get("/api/v1/vip/plans").json())

    customer = client.post(
        "/api/v1/customers", json={"name": "VIP Customer", "pin": "1234"}
    ).json()
    sale = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "VIP", "item_name": "ignored",
            "vip_plan_id": plan_id, "payment_method": "CASH", "request_id": "VIP-SALE-1",
        },
    )
    assert sale.status_code == 201
    assert sale.json()["amount"] == 150000
    with get_connection() as conn:
        assert conn.execute("SELECT 1 FROM customer_vip WHERE customer_id = ?", (customer["id"],)).fetchone() is None

    confirmed = client.post(
        f"/api/v1/sales/{sale.json()['id']}/confirm",
        json={"reference": "VIP-CASH", "request_id": "VIP-PAY-1"},
    )
    assert confirmed.status_code == 200
    with get_connection() as conn:
        vip = conn.execute("SELECT * FROM customer_vip WHERE customer_id = ?", (customer["id"],)).fetchone()
    assert vip["status"] == "ACTIVE"
    assert vip["expires_at"]
    assert client.get(f"/api/v1/customers/{customer['id']}/credit").json()["total_seconds"] == 0