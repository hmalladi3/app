import pytest
from conftest import BASE_URL

def test_create_review(api_client, test_account, test_service, base_url):
    """Test review creation"""
    review_data = {
        "rating": 4,
        "title": "Good service",
        "body": "Would recommend"
    }
    
    response = api_client.post(
        f"{base_url}/api/services/{test_service['id']}/reviews?client_id={test_account['id']}", 
        json=review_data
    )
    assert response.status_code == 200
    
    review = response.json()
    assert review["rating"] == review_data["rating"]
    assert review["title"] == review_data["title"]
    
    return review

def test_get_service_reviews(api_client, test_service, test_review):
    """Test getting reviews for a service"""
    response = api_client.get(f"{BASE_URL}/api/services/{test_service['id']}/reviews")
    assert response.status_code == 200
    
    reviews = response.json()
    assert len(reviews) > 0
    assert any(r["id"] == test_review["id"] for r in reviews)

def test_get_service_rating(api_client, test_service, test_review):
    """Test getting average rating for a service"""
    response = api_client.get(f"{BASE_URL}/api/services/{test_service['id']}/rating")
    assert response.status_code == 200
    
    rating_data = response.json()
    assert "average_rating" in rating_data
    assert isinstance(rating_data["average_rating"], (int, float))

def test_delete_review(api_client, test_review, test_account):
    """Test review deletion"""
    response = api_client.delete(
        f"{BASE_URL}/api/reviews/{test_review['id']}?client_id={test_account['id']}"
    )
    assert response.status_code == 200
