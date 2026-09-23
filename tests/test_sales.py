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


def test_unknown_payment_never_activates_credit(client):
    customer = client.post(
        "/api/v1/customers", json={"name": "Unknown Payment", "pin": "1234"}
    ).json()
    sale = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "GAMING", "item_name": "Unknown",
            "duration_seconds": 1800, "amount": 40000, "payment_method": "CARD",
            "request_id": "SALE-UNKNOWN-1",
        },
    ).json()

    unknown = client.post(
        f"/api/v1/sales/{sale['id']}/unknown",
        json={"reference": "POS-TIMEOUT", "request_id": "PAY-UNKNOWN-1"},
    )
    assert unknown.status_code == 200
    assert unknown.json()["payment_status"] == "UNKNOWN"
    assert client.get(f"/api/v1/customers/{customer['id']}/credit").json()["total_seconds"] == 0

    failed = client.post(
        f"/api/v1/sales/{sale['id']}/resolve",
        json={"status": "FAILED", "reference": "POS-DECLINED", "request_id": "PAY-RESOLVE-1"},
    )
    assert failed.status_code == 200
    assert failed.json()["payment_status"] == "FAILED"


def test_refund_requires_approval_and_reverses_unused_credit(client, admin_client):
    customer = client.post(
        "/api/v1/customers", json={"name": "Refund Customer", "pin": "1234"}
    ).json()
    sale = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "GAMING", "item_name": "Refundable",
            "duration_seconds": 900, "amount": 20000, "payment_method": "CASH",
            "request_id": "SALE-REFUND-1",
        },
    ).json()
    assert client.post(
        f"/api/v1/sales/{sale['id']}/confirm",
        json={"reference": "CASH-REFUND-1", "request_id": "PAY-REFUND-1"},
    ).status_code == 200
    assert client.post(
        f"/api/v1/sales/{sale['id']}/refund",
        json={"reason": "Customer cancellation", "request_id": "REFUND-REQUEST-1"},
    ).json()["payment_status"] == "REFUND_PENDING"

    approved = admin_client.post(
        f"/api/v1/sales/{sale['id']}/refund/approve",
        json={"reason": "Approved by owner", "request_id": "REFUND-APPROVE-1"},
    )
    assert approved.status_code == 200
    assert approved.json()["payment_status"] == "REFUNDED"
    assert client.get(f"/api/v1/customers/{customer['id']}/credit").json()["total_seconds"] == 0