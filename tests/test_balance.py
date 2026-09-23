def test_balance_recharge_debit_and_insufficient_payment(client):
    customer = client.post(
        "/api/v1/customers", json={"name": "Balance Customer", "pin": "1234"}
    ).json()

    recharge = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "RECHARGE", "item_name": "Recharge",
            "amount": 5000, "payment_method": "CASH", "request_id": "BALANCE-RECHARGE-1",
        },
    ).json()
    assert client.post(
        f"/api/v1/sales/{recharge['id']}/confirm",
        json={"reference": "CASH-5000", "request_id": "BALANCE-PAY-1"},
    ).status_code == 200
    assert client.get(f"/api/v1/customers/{customer['id']}/balance").json()["amount"] == 5000

    purchase = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "FOOD", "item_name": "Snack",
            "amount": 3000, "payment_method": "BALANCE", "request_id": "BALANCE-SALE-1",
        },
    ).json()
    confirmed = client.post(
        f"/api/v1/sales/{purchase['id']}/confirm",
        json={"request_id": "BALANCE-PAY-2"},
    )
    assert confirmed.status_code == 200
    assert client.get(f"/api/v1/customers/{customer['id']}/balance").json()["amount"] == 2000

    repeated = client.post(
        f"/api/v1/sales/{purchase['id']}/confirm",
        json={"request_id": "BALANCE-PAY-2"},
    )
    assert repeated.status_code == 200
    assert client.get(f"/api/v1/customers/{customer['id']}/balance").json()["amount"] == 2000

    expensive = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "FOOD", "item_name": "Expensive",
            "amount": 2500, "payment_method": "BALANCE", "request_id": "BALANCE-SALE-2",
        },
    ).json()
    rejected = client.post(
        f"/api/v1/sales/{expensive['id']}/confirm",
        json={"request_id": "BALANCE-PAY-3"},
    )
    assert rejected.status_code == 409
    assert client.get(f"/api/v1/customers/{customer['id']}/balance").json()["amount"] == 2000