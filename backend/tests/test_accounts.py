import pytest
import requests

BASE_URL = "http://localhost:8000"

def test_create_account(api_client):
    """Test account creation"""
    data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "pass123"
    }
    
    response = api_client.post(f"{BASE_URL}/api/accounts", json=data)
    assert response.status_code == 200
    
    account = response.json()
    assert account["username"] == data["username"]
    assert "id" in account
    
    # Cleanup
    api_client.delete(f"{BASE_URL}/api/accounts/{account['id']}")

def test_login(api_client, test_account):
    """Test login functionality"""
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = api_client.post(f"{BASE_URL}/api/login", json=data)
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_account(api_client, test_account):
    """Test getting account details"""
    response = api_client.get(f"{BASE_URL}/api/accounts/{test_account['id']}")
    assert response.status_code == 200
    assert response.json()["username"] == test_account["username"]

def test_update_account(api_client, test_account):
    """Test account update"""
    update_data = {
        "username": "updated_user"
    }
    
    response = api_client.put(
        f"{BASE_URL}/api/accounts/{test_account['id']}", 
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["username"] == update_data["username"]

def test_delete_account(api_client, test_account):
    """Test account deletion"""
    response = api_client.delete(f"{BASE_URL}/api/accounts/{test_account['id']}")
    assert response.status_code == 200
    
    # Verify account is gone
    response = api_client.get(f"{BASE_URL}/api/accounts/{test_account['id']}")
    assert response.status_code == 404
