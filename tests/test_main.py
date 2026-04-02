from fastapi.testclient import TestClient
from main import app

def test_read_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "PR7 Security Admin API is Online"}

def test_auth_login_invalid():
    # Test invalid login
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
