import pytest
from tests.conftest import BASE_URL

def test_basic_search(api_client, test_account, test_service):
    """Test basic search functionality"""
    response = api_client.get(f"{BASE_URL}/api/search?query={test_service['title']}")
    assert response.status_code == 200
    
    results = response.json()
    assert "services" in results
    assert len(results["services"]) > 0
    assert any(s["id"] == test_service["id"] for s in results["services"])

def test_advanced_search(api_client, test_account, test_service):
    """Test advanced search with filters"""
    # Add hashtags to test account
    api_client.post(
        f"{BASE_URL}/api/accounts/{test_account['id']}/hashtags", 
        json=["developer"]
    )
    
    response = api_client.get(
        f"{BASE_URL}/api/search/advanced",
        params={
            "query": test_service["title"],
            "min_price": test_service["price"] - 1000,
            "max_price": test_service["price"] + 1000,
            "hashtags": ["developer"],
            "sort": "price_high"
        }
    )
    assert response.status_code == 200
    
    results = response.json()
    assert len(results) > 0
    assert any(s["id"] == test_service["id"] for s in results)
