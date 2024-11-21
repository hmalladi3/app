import pytest
from tests.conftest import BASE_URL

def test_add_hashtags(api_client, test_account):
    """Test adding hashtags to an account"""
    tags = ["developer", "webdesign"]
    
    response = api_client.post(
        f"{BASE_URL}/api/accounts/{test_account['id']}/hashtags", 
        json=tags
    )
    assert response.status_code == 200
    
    # Verify hashtags were added
    response = api_client.get(f"{BASE_URL}/api/accounts/{test_account['id']}/hashtags")
    assert response.status_code == 200
    account_tags = response.json()
    assert len(account_tags) == len(tags)
    assert all(tag["tag"] in tags for tag in account_tags)

def test_remove_hashtag(api_client, test_account):
    """Test removing a hashtag from an account"""
    # First add a hashtag
    tags = ["testhashtag"]
    api_client.post(
        f"{BASE_URL}/api/accounts/{test_account['id']}/hashtags", 
        json=tags
    )
    
    # Then remove it
    response = api_client.delete(
        f"{BASE_URL}/api/accounts/{test_account['id']}/hashtags/testhashtag"
    )
    assert response.status_code == 200

def test_search_hashtags(api_client, test_account):
    """Test hashtag search"""
    # Add test hashtags
    tags = ["python", "programming"]
    api_client.post(
        f"{BASE_URL}/api/accounts/{test_account['id']}/hashtags", 
        json=tags
    )
    
    # Search for them
    response = api_client.get(f"{BASE_URL}/api/hashtags/search?query=program")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
