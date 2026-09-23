def test_create_and_get_customer(client):
    create = client.post(
        "/api/v1/customers",
        json={
            "name": "Ali Test",
            "mobile": "09120000000",
            "gaming_name": "AliGamer",
            "pin": "1234",
        },
    )
    assert create.status_code == 201
    data = create.json()
    assert data["name"] == "Ali Test"
    assert data["customer_number"] >= 1040
    assert data["status"] == "ACTIVE"

    by_number = client.get(f"/api/v1/customers/by-number/{data['customer_number']}")
    assert by_number.status_code == 200
    assert by_number.json()["id"] == data["id"]


def test_search_customer(client):
    client.post(
        "/api/v1/customers",
        json={"name": "Search Me", "pin": "5678"},
    )
    response = client.get("/api/v1/customers/search", params={"q": "Search"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(c["name"] == "Search Me" for c in body["items"])
