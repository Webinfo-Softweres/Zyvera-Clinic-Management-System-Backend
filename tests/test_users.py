def test_get_users_unauthorized(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401
