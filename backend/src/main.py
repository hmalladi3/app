from fastapi import FastAPI, HTTPException, Query, Path, Body
from typing import List, Optional
from src.services.account import AccountService
from src.services.service import ServiceService
from src.services.review import ReviewService
from src.services.hashtag import HashtagService
from pydantic import BaseModel, EmailStr, conint, Field
from src.db import init_db, get_db_session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize services
account_service = AccountService()
service_service = ServiceService()
review_service = ReviewService()
hashtag_service = HashtagService()

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    logger.info("Initializing database...")
    try:
        init_db()  # Create tables if they don't exist
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

# Pydantic models for request validation
class AccountCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class AccountUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class ServiceCreate(BaseModel):
    title: str
    description: str
    price: int  # in cents

class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)  # Rating between 1-5
    title: str
    body: str

# Account endpoints
@app.post("/api/accounts")
async def create_account(account: AccountCreate):
    try:
        result = account_service.create_account(
            username=account.username,
            email=account.email,
            password=account.password
        )
        return result
    except Exception as e:
        # Add detailed error logging
        import traceback
        print(f"Error creating account: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/login")
async def login(username: str = Body(...), password: str = Body(...)):
    try:
        return account_service.login(username, password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/api/accounts/{account_id}")
async def get_account(account_id: int = Path(...)):
    account = account_service.get_account_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.put("/api/accounts/{account_id}")
async def update_account(account_id: int, update_data: AccountUpdate):
    try:
        return account_service.update_account(
            id=account_id,
            username=update_data.username,
            email=update_data.email,
            password=update_data.password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Service endpoints
@app.post("/api/services")
async def create_service(
    account_id: int = Query(...),
    service: ServiceCreate = Body(...)
):
    try:
        return service_service.create_service(
            account_id=account_id,
            title=service.title,
            description=service.description,
            price=service.price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/services/{service_id}")
async def get_service(service_id: int):
    service = service_service.get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@app.get("/api/accounts/{account_id}/services")
async def get_account_services(account_id: int):
    return service_service.get_services_by_account(account_id)

@app.get("/api/services/search")
async def search_services(
    keyword: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None
):
    return service_service.search_services(
        keyword=keyword,
        min_price=min_price,
        max_price=max_price
    )

# Review endpoints
@app.post("/api/services/{service_id}/reviews")
async def create_review(
    service_id: int,
    client_id: int = Query(...),
    review: ReviewCreate = Body(...)
):
    try:
        return review_service.create_review(
            client_id=client_id,
            service_id=service_id,
            rating=review.rating,
            title=review.title,
            body=review.body
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/services/{service_id}/reviews")
async def get_service_reviews(service_id: int):
    return review_service.get_reviews_by_service(service_id)

@app.get("/api/services/{service_id}/rating")
async def get_service_rating(service_id: int):
    return {"average_rating": review_service.get_average_rating(service_id=service_id)}

# Hashtag endpoints
@app.post("/api/accounts/{account_id}/hashtags")
async def add_hashtags(
    account_id: int,
    tags: List[str] = Body(...)
):
    try:
        return hashtag_service.add_hashtags_to_account(account_id, tags)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/accounts/{account_id}/hashtags")
async def get_account_hashtags(account_id: int):
    try:
        return hashtag_service.get_account_hashtags(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/hashtags/search")
async def search_hashtags(query: str = Query(...)):
    return hashtag_service.search_hashtags(query)

@app.get("/api/hashtags/{tag}/accounts")
async def get_accounts_by_hashtag(tag: str):
    return hashtag_service.get_accounts_by_hashtag(tag)

@app.delete("/api/accounts/{account_id}/hashtags/{tag}")
async def remove_hashtag(
    account_id: int = Path(..., description="ID of the account"),
    tag: str = Path(..., description="Hashtag to remove")
):
    """
    Remove a hashtag from an account
    """
    try:
        result = hashtag_service.remove_hashtag_from_account(account_id, tag)
        if result:
            return {"message": f"Hashtag #{tag} removed from account {account_id}"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Hashtag #{tag} not found for account {account_id}"
            )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Combined search endpoint
@app.get("/api/search")
async def search_all(
    query: str = Query(...),
    filter_type: Optional[str] = Query(None, enum=['accounts', 'services', 'hashtags'])
):
    """
    Search across accounts, services, and hashtags
    """
    results = {}
    
    # Search services
    services = service_service.search_services(keyword=query)
    if not filter_type or filter_type == 'services':
        results['services'] = services
    
    # Search hashtags
    hashtags = hashtag_service.search_hashtags(query)
    if not filter_type or filter_type == 'hashtags':
        results['hashtags'] = hashtags
    
    # Search accounts through hashtags
    accounts = hashtag_service.get_accounts_by_hashtag(query)
    if not filter_type or filter_type == 'accounts':
        results['accounts'] = accounts
    
    return results

# Advanced search endpoint
@app.get("/api/search/advanced")
async def advanced_search(
    query: Optional[str] = None,
    service_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    hashtags: List[str] = Query([]),
    sort: str = Query("relevance", enum=["relevance", "price_low", "price_high", "rating"])
):
    """
    Advanced search with multiple filters and sorting options
    """
    # Start with service search
    services = service_service.search_services(
        keyword=query or service_type,
        min_price=min_price,
        max_price=max_price
    )
    
    # Filter by hashtags if specified
    if hashtags:
        filtered_services = []
        for service in services:
            account_tags = hashtag_service.get_account_hashtags(service['account_id'])
            account_tag_names = [tag['tag'] for tag in account_tags]
            if any(tag in account_tag_names for tag in hashtags):
                filtered_services.append(service)
        services = filtered_services
    
    # Sort results
    if sort == "price_low":
        services.sort(key=lambda x: x['price'])
    elif sort == "price_high":
        services.sort(key=lambda x: x['price'], reverse=True)
    elif sort == "rating":
        services.sort(
            key=lambda x: review_service.get_average_rating(service_id=x['id']),
            reverse=True
        )
    
    return services

# Add these new endpoints:

# Delete Account
@app.delete("/api/accounts/{account_id}")
async def delete_account(account_id: int = Path(..., description="ID of the account to delete")):
    """
    Delete an account and all associated services, reviews, and hashtags
    """
    try:
        result = account_service.delete_account(account_id)
        if result:
            return {"message": f"Account {account_id} successfully deleted"}
        raise HTTPException(status_code=404, detail="Account not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete Service
@app.delete("/api/services/{service_id}")
async def delete_service(
    service_id: int = Path(..., description="ID of the service to delete"),
    account_id: int = Query(..., description="ID of the account that owns the service")
):
    """
    Delete a service and its associated reviews
    """
    try:
        result = service_service.delete_service(service_id, account_id)
        if result:
            return {"message": f"Service {service_id} successfully deleted"}
        raise HTTPException(status_code=404, detail="Service not found")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

# Delete Review
@app.delete("/api/reviews/{review_id}")
async def delete_review(
    review_id: int = Path(..., description="ID of the review to delete"),
    client_id: int = Query(..., description="ID of the client who wrote the review")
):
    """
    Delete a review (only by the client who created it)
    """
    try:
        result = review_service.delete_review(review_id, client_id)
        if result:
            return {"message": f"Review {review_id} successfully deleted"}
        raise HTTPException(status_code=404, detail="Review not found")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)