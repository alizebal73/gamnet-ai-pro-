def test_payment_first_then_credit_activation(client, admin_client):
    customer = client.post(
        "/api/v1/customers", json={"name": "Sale Customer", "pin": "1234"}
    ).json()
    sale_payload = {
        "customer_id": customer["id"],
        "item_type": "GAMING",
        "item_name": "1 Hour Gaming",
        "duration_seconds": 3600,
        "amount": 80000,
        "payment_method": "CASH",
        "request_id": "SALE-TEST-1",
    }

    created = client.post("/api/v1/sales", json=sale_payload)
    assert created.status_code == 201
    sale = created.json()
    assert sale["status"] == "CREATED"
    assert sale["payment_status"] == "PENDING"
    assert client.get(f"/api/v1/customers/{customer['id']}/credit").json()["total_seconds"] == 0

    duplicate = client.post("/api/v1/sales", json=sale_payload)
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == sale["id"]

    confirmed = client.post(
        f"/api/v1/sales/{sale['id']}/confirm",
        json={"reference": "CASH-REF-1", "request_id": "PAY-CONFIRM-1"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "PAID"
    assert confirmed.json()["payment_status"] == "PAID"
    assert client.get(f"/api/v1/customers/{customer['id']}/credit").json()["total_seconds"] == 3600

    repeated_confirm = client.post(
        f"/api/v1/sales/{sale['id']}/confirm",
        json={"reference": "CASH-REF-1", "request_id": "PAY-CONFIRM-1"},
    )
    assert repeated_confirm.status_code == 200
    assert client.get(f"/api/v1/customers/{customer['id']}/credit").json()["total_seconds"] == 3600