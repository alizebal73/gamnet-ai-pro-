def test_credit_grant_is_ledger_backed_and_idempotent(client, admin_client):
    customer_response = client.post(
        "/api/v1/customers", json={"name": "Credit Customer", "pin": "1234"}
    )
    customer_id = customer_response.json()["id"]
    payload = {
        "credit_type": "PAID",
        "seconds": 3600,
        "source": "SALE-TEST-1",
        "request_id": "GRANT-TEST-1",
    }

    first = admin_client.post(f"/api/v1/customers/{customer_id}/credit", json=payload)
    second = admin_client.post(f"/api/v1/customers/{customer_id}/credit", json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["entitlement_id"] == second.json()["entitlement_id"]
    assert second.json()["total_seconds"] == 3600

    balance = client.get(f"/api/v1/customers/{customer_id}/credit")
    assert balance.status_code == 200
    assert balance.json()["total_seconds"] == 3600


def test_operator_cannot_grant_credit(client):
    customer_response = client.post(
        "/api/v1/customers", json={"name": "Protected Credit", "pin": "1234"}
    )

    response = client.post(
        f"/api/v1/customers/{customer_response.json()['id']}/credit",
        json={
            "credit_type": "ADMIN_ADJUSTMENT",
            "seconds": 60,
            "source": "MANUAL",
            "request_id": "GRANT-DENIED-1",
        },
    )

    assert response.status_code == 403