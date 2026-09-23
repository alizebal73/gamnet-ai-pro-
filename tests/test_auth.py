def test_login_and_current_user(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["username"] == "test_operator"
    assert "OPERATOR" in response.json()["roles"]


def test_customer_api_requires_authentication(client):
    client.headers.pop("Authorization")

    response = client.get("/api/v1/customers/search", params={"q": "test"})

    assert response.status_code == 401