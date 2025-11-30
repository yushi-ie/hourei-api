import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app
from services.auth import fake_users_db, get_password_hash

client = TestClient(app)

# Setup fake user for testing
fake_users_db["testuser"] = {
    "username": "testuser",
    "full_name": "Test User",
    "email": "test@example.com",
    "hashed_password": get_password_hash("testpassword"),
    "disabled": False,
}

def test_login():
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_incorrect_password():
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401

def test_read_users_me():
    # Get token first
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    token = response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

@patch("routers.photos.storage_service")
def test_upload_photo(mock_storage_service):
    # Mock upload_file method
    mock_storage_service.upload_file.return_value = "testuser/test.jpg"

    # Get token first
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    token = response.json()["access_token"]

    # Upload file
    files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
    response = client.post(
        "/photos/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Photo uploaded successfully"
    assert "testuser/test.jpg" in response.json()["filename"]
