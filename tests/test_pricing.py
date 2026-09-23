def test_server_pricing_quote_and_sale_snapshot(client):
    quote = client.post(
        "/api/v1/pricing/quote",
        json={"item_type": "GAMING", "duration_seconds": 3600},
    )
    assert quote.status_code == 200
    assert quote.json()["amount"] == 80000

    customer = client.post(
        "/api/v1/customers", json={"name": "Priced Customer", "pin": "1234"}
    ).json()
    sale = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "GAMING", "item_name": "30 Minutes",
            "duration_seconds": 1800, "payment_method": "CASH", "request_id": "SALE-PRICE-1",
        },
    )
    assert sale.status_code == 201
    assert sale.json()["amount"] == 40000
    assert sale.json()["price_snapshot"] == 40000
    assert sale.json()["pricing_rule_id"] == "PRICE-GAMING-1800"


def test_manual_gaming_amount_must_match_rule(client):
    customer = client.post(
        "/api/v1/customers", json={"name": "Price Guard Customer", "pin": "1234"}
    ).json()
    response = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "GAMING", "item_name": "Invalid Price",
            "duration_seconds": 3600, "amount": 1, "payment_method": "CASH",
            "request_id": "SALE-PRICE-GUARD-1",
        },
    )
    assert response.status_code == 409