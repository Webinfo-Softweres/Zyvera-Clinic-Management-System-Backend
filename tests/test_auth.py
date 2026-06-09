def test_login_missing_credentials(client):
    response = client.post("/api/v1/auth/login", json={})
    assert response.status_code == 422
