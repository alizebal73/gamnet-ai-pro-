from gamenet.server.db import get_connection


def test_package_catalog_and_purchase_creates_expiring_entitlement(client, admin_client):
    created = admin_client.post(
        "/api/v1/packages",
        json={
            "name": "Weekend Package", "duration_seconds": 3600,
            "price": 70000, "expiry_days": 7, "bonus_seconds": 600,
        },
    )
    assert created.status_code == 201
    package = created.json()
    assert package["active"] is True

    listed = client.get("/api/v1/packages")
    assert listed.status_code == 200
    assert any(item["id"] == package["id"] for item in listed.json())

    customer = client.post(
        "/api/v1/customers", json={"name": "Package Customer", "pin": "1234"}
    ).json()
    sale = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "PACKAGE",
            "item_name": "ignored", "package_id": package["id"],
            "payment_method": "CASH", "request_id": "PACKAGE-SALE-1",
        },
    )
    assert sale.status_code == 201
    assert sale.json()["amount"] == 70000
    assert sale.json()["duration_seconds"] == 4200

    confirmed = client.post(
        f"/api/v1/sales/{sale.json()['id']}/confirm",
        json={"reference": "PACKAGE-CASH", "request_id": "PACKAGE-PAY-1"},
    )
    assert confirmed.status_code == 200
    assert client.get(f"/api/v1/customers/{customer['id']}/credit").json()["total_seconds"] == 4200

    with get_connection() as conn:
        entitlement = conn.execute(
            "SELECT expires_at, credit_type FROM entitlements WHERE customer_id = ?",
            (customer["id"],),
        ).fetchone()
    assert entitlement["credit_type"] == "PACKAGE"
    assert entitlement["expires_at"]