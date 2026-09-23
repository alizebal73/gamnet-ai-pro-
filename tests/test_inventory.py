def test_inventory_sale_decrements_stock_once(client, admin_client):
    item = admin_client.post(
        "/api/v1/inventory",
        json={"name": "Cola", "sku": "COLA-1", "purchase_price": 500, "sale_price": 1000, "initial_stock": 1},
    )
    assert item.status_code == 201
    item_id = item.json()["id"]
    customer = client.post(
        "/api/v1/customers", json={"name": "Inventory Customer", "pin": "1234"}
    ).json()
    sale = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "FOOD", "item_name": "ignored",
            "inventory_item_id": item_id, "payment_method": "CASH", "request_id": "INV-SALE-1",
        },
    )
    assert sale.status_code == 201
    assert sale.json()["amount"] == 1000
    confirmed = client.post(
        f"/api/v1/sales/{sale.json()['id']}/confirm",
        json={"reference": "CASH-COLA", "request_id": "INV-PAY-1"},
    )
    assert confirmed.status_code == 200
    assert client.get("/api/v1/inventory").json()[0]["stock"] == 0
    repeated = client.post(
        f"/api/v1/sales/{sale.json()['id']}/confirm",
        json={"reference": "CASH-COLA", "request_id": "INV-PAY-1"},
    )
    assert repeated.status_code == 200
    assert client.get("/api/v1/inventory").json()[0]["stock"] == 0

    empty_sale = client.post(
        "/api/v1/sales",
        json={
            "customer_id": customer["id"], "item_type": "FOOD", "item_name": "ignored",
            "inventory_item_id": item_id, "payment_method": "CASH", "request_id": "INV-SALE-2",
        },
    )
    assert empty_sale.status_code == 409