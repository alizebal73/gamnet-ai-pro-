def test_daily_report_returns_owner_visibility_shape(client):
    response = client.get("/api/v1/reports/daily", params={"day": "2020-01-01"})

    assert response.status_code == 200
    body = response.json()
    assert body["day"] == "2020-01-01"
    assert body["revenue"] == 0
    assert body["unknown_payments"] == 0
    assert "cash_difference" in body