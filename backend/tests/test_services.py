import pytest
from tests.conftest import BASE_URL

def test_create_service(api_client, test_account):
    """Test service creation"""
    service_data = {
        "title": "Web Development",
        "description": "Professional web development services",
        "price": 10000  # $100.00
    }
    
    response = api_client.post(
        f"{BASE_URL}/api/services?account_id={test_account['id']}", 
        json=service_data
    )
    assert response.status_code == 200
    
    service = response.json()
    assert service["title"] == service_data["title"]
    assert service["price"] == service_data["price"]
    
    return service

def test_search_services(api_client, test_account):
    """Test service search"""
    # Create a test service first
    service = test_create_service(api_client, test_account)
    
    # Search for it using query parameter instead of keyword
    response = api_client.get(
        f"{BASE_URL}/api/search",  # Updated endpoint
        params={"query": "Web Development"}  # Changed from keyword to query
    )
    assert response.status_code == 200
    results = response.json()
    assert "services" in results  # Check for services key in response
    assert len(results["services"]) > 0
    assert any(s["id"] == service["id"] for s in results["services"])
