import pytest
from tests.conftest import BASE_URL
import uuid

def test_create_review(api_client, test_account):
    """Test review creation"""
    # Create service owner account with unique username
    unique_suffix = str(uuid.uuid4())[:8]
    other_account_data = {
        "username": f"serviceowner_{unique_suffix}",
        "email": f"service_{unique_suffix}@example.com",
        "password": "pass123"
    }
    response = api_client.post(f"{BASE_URL}/api/accounts", json=other_account_data)
    assert response.status_code == 200, f"Failed to create account: {response.text}"
    other_account = response.json()
    
    # Create service with other account
    service_data = {
        "title": "Test Service",
        "description": "A test service",
        "price": 9999
    }
    response = api_client.post(
        f"{BASE_URL}/api/services?account_id={other_account['id']}", 
        json=service_data
    )
    assert response.status_code == 200, f"Failed to create service: {response.text}"
    service = response.json()
    
    # Create review as test_account
    review_data = {
        "rating": 4,
        "title": "Good service",
        "body": "Would recommend"
    }
    
    response = api_client.post(
        f"{BASE_URL}/api/services/{service['id']}/reviews?client_id={test_account['id']}", 
        json=review_data
    )
    assert response.status_code == 200, f"Failed to create review: {response.text}"
    
    review = response.json()
    assert review["rating"] == review_data["rating"]
    assert review["title"] == review_data["title"]
    
    # Cleanup the service owner account (which will cascade delete the service)
    api_client.delete(f"{BASE_URL}/api/accounts/{other_account['id']}")
    return review

def test_get_service_reviews(api_client, test_account):
    """Test getting reviews for a service"""
    review = test_create_review(api_client, test_account)
    
    response = api_client.get(f"{BASE_URL}/api/services/{review['service_id']}/reviews")
    assert response.status_code == 200
    
    reviews = response.json()
    assert len(reviews) > 0

def test_get_service_rating(api_client, test_account):
    """Test getting average rating for a service"""
    review = test_create_review(api_client, test_account)
    
    response = api_client.get(f"{BASE_URL}/api/services/{review['service_id']}/rating")
    assert response.status_code == 200
    
    rating_data = response.json()
    assert "average_rating" in rating_data
    assert isinstance(rating_data["average_rating"], (int, float))

def test_delete_review(api_client, test_account):
    """Test review deletion"""
    review = test_create_review(api_client, test_account)
    print(f"\nReview to delete: {review}")
    
    # Delete review using account_id instead of client_id for consistency
    response = api_client.delete(
        f"{BASE_URL}/api/reviews/{review['id']}?account_id={test_account['id']}"
    )
    
    assert response.status_code == 200, f"Failed to delete review: {response.text}"
    
    # Verify deletion
    get_response = api_client.get(f"{BASE_URL}/api/services/{review['service_id']}/reviews")
    assert get_response.status_code == 200
    reviews = get_response.json()
    assert not any(r['id'] == review['id'] for r in reviews), "Review still exists after deletion"
