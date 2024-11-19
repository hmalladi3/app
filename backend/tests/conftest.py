import pytest
import requests
from typing import Generator, Dict
from src.db import engine, Base, SessionLocal
from src.models import Account, Service, Review, Hashtag  # Import all models

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:8000"

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup and teardown test database for all tests"""
    print("\nSetting up test database...")
    # Create all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    yield
    
    print("\nCleaning up test database...")
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Get a database session for each test"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def api_client():
    """Provides a configured requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture
def test_account(api_client, base_url) -> Generator[Dict, None, None]:
    """Creates a test account and cleans it up after"""
    # Generate unique username
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    account_data = {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "testpass123"
    }
    
    response = api_client.post(f"{base_url}/api/accounts", json=account_data)
    
    if response.status_code != 200:
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        raise Exception(f"Failed to create test account: {response.text}")
    
    account = response.json()
    yield account
    
    try:
        api_client.delete(f"{base_url}/api/accounts/{account['id']}")
    except Exception as e:
        print(f"Error cleaning up test account: {str(e)}")

@pytest.fixture
def test_service(api_client, test_account) -> Generator[Dict, None, None]:
    """Creates a test service and cleans it up after"""
    service_data = {
        "title": "Test Service",
        "description": "A test service",
        "price": 9999
    }
    response = api_client.post(
        f"{base_url}/api/services?account_id={test_account['id']}", 
        json=service_data
    )
    service = response.json()
    yield service
    try:
        api_client.delete(
            f"{base_url}/api/services/{service['id']}?account_id={test_account['id']}"
        )
    except:
        pass

@pytest.fixture
def test_review(api_client, test_service, test_account) -> Generator[Dict, None, None]:
    """Creates a test review and cleans it up after"""
    review_data = {
        "rating": 5,
        "title": "Great service!",
        "body": "Really enjoyed working with this provider"
    }
    response = api_client.post(
        f"{base_url}/api/services/{test_service['id']}/reviews?client_id={test_account['id']}", 
        json=review_data
    )
    review = response.json()
    yield review
    try:
        api_client.delete(
            f"{base_url}/api/reviews/{review['id']}?client_id={test_account['id']}"
        )
    except:
        pass
