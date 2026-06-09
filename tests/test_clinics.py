def test_get_clinics_unauthorized(client):
    response = client.get("/api/v1/clinics")
    assert response.status_code == 401
