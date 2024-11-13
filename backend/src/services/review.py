import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.db import get_db_session
from src.models import Review, Account, Service
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

class ReviewService:
    def create_review(self, client_id: int, service_id: int, rating: int, title: str, body: str):
        """
        Create a new review.
        client_id: The ID of the user writing the review
        service_id: The ID of the service being reviewed
        rating: Integer 1-5
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        with get_db_session() as session:
            # Get the service and its account
            service = session.get(Service, service_id)
            if not service:
                raise ValueError("Service not found")

            # Ensure client exists
            client = session.get(Account, client_id)
            if not client:
                raise ValueError("Client account not found")

            # Prevent self-reviews
            if client_id == service.account_id:
                raise ValueError("Cannot review your own service")

            # Check if user has already reviewed this service
            existing_review = session.query(Review).filter(
                Review.client_id == client_id,
                Review.service_id == service_id
            ).first()
            if existing_review:
                raise ValueError("You have already reviewed this service")

            review = Review(
                account_id=service.account_id,  # The service provider's ID
                client_id=client_id,           # The reviewer's ID
                service_id=service_id,
                rating=rating,
                title=title,
                body=body
            )
            session.add(review)
            
            try:
                session.commit()
                return {
                    'id': review.id,
                    'account_id': review.account_id,
                    'client_id': review.client_id,
                    'service_id': review.service_id,
                    'rating': review.rating,
                    'title': review.title,
                    'body': review.body,
                    'created_at': review.created_at,
                    'updated_at': review.updated_at
                }
            except IntegrityError:
                session.rollback()
                raise ValueError("An error occurred while creating the review")

    def get_review_by_id(self, review_id: int):
        with get_db_session() as session:
            review = session.get(Review, review_id)
            if review:
                return {
                    'id': review.id,
                    'account_id': review.account_id,
                    'client_id': review.client_id,
                    'service_id': review.service_id,
                    'rating': review.rating,
                    'title': review.title,
                    'body': review.body,
                    'created_at': review.created_at,
                    'updated_at': review.updated_at
                }
            return None

    def get_reviews_by_service(self, service_id: int):
        with get_db_session() as session:
            reviews = session.query(Review).filter(Review.service_id == service_id).all()
            return [{
                'id': review.id,
                'account_id': review.account_id,
                'client_id': review.client_id,
                'service_id': review.service_id,
                'rating': review.rating,
                'title': review.title,
                'body': review.body,
                'created_at': review.created_at,
                'updated_at': review.updated_at
            } for review in reviews]

    def get_reviews_by_account(self, account_id: int):
        """Get all reviews for services provided by this account"""
        with get_db_session() as session:
            reviews = session.query(Review).filter(Review.account_id == account_id).all()
            return [{
                'id': review.id,
                'account_id': review.account_id,
                'client_id': review.client_id,
                'service_id': review.service_id,
                'rating': review.rating,
                'title': review.title,
                'body': review.body,
                'created_at': review.created_at,
                'updated_at': review.updated_at
            } for review in reviews]

    def get_reviews_by_client(self, client_id: int):
        """Get all reviews written by this client"""
        with get_db_session() as session:
            reviews = session.query(Review).filter(Review.client_id == client_id).all()
            return [{
                'id': review.id,
                'account_id': review.account_id,
                'client_id': review.client_id,
                'service_id': review.service_id,
                'rating': review.rating,
                'title': review.title,
                'body': review.body,
                'created_at': review.created_at,
                'updated_at': review.updated_at
            } for review in reviews]

    def update_review(self, review_id: int, rating: int = None, title: str = None, body: str = None):
        with get_db_session() as session:
            review = session.get(Review, review_id)
            if not review:
                raise ValueError("Review not found")

            if rating is not None:
                if not 1 <= rating <= 5:
                    raise ValueError("Rating must be between 1 and 5")
                review.rating = rating
            if title is not None:
                review.title = title
            if body is not None:
                review.body = body

            try:
                session.commit()
                return {
                    'id': review.id,
                    'account_id': review.account_id,
                    'client_id': review.client_id,
                    'service_id': review.service_id,
                    'rating': review.rating,
                    'title': review.title,
                    'body': review.body,
                    'created_at': review.created_at,
                    'updated_at': review.updated_at
                }
            except IntegrityError:
                session.rollback()
                raise ValueError("An error occurred while updating the review")

    def delete_review(self, review_id: int):
        with get_db_session() as session:
            review = session.get(Review, review_id)
            if review:
                session.delete(review)
                session.commit()
                return True
            return False

    def get_average_rating(self, service_id: int = None, account_id: int = None):
        """Get the average rating for a service or account"""
        with get_db_session() as session:
            query = session.query(func.avg(Review.rating))
            if service_id:
                query = query.filter(Review.service_id == service_id)
            elif account_id:
                query = query.filter(Review.account_id == account_id)
            else:
                raise ValueError("Must provide either service_id or account_id")
            
            avg_rating = query.scalar()
            return float(avg_rating) if avg_rating else 0.0


if __name__ == "__main__":
    import unittest
    from src.db import init_db, drop_db
    from src.services.account import AccountService
    from src.services.service import ServiceService

    class TestReviewService(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            print("Initializing test database...")
            init_db()
            cls.review_service = ReviewService()
            cls.account_service = AccountService()
            cls.service_service = ServiceService()

            # Create test accounts and service
            cls.provider = cls.account_service.create_account(
                username="provider",
                email="provider@example.com",
                password="testpass123"
            )
            cls.client = cls.account_service.create_account(
                username="client",
                email="client@example.com",
                password="testpass123"
            )
            cls.service = cls.service_service.create_service(
                account_id=cls.provider['id'],
                title="Test Service",
                description="A service to review",
                price=1000
            )

        @classmethod
        def tearDownClass(cls):
            print("Cleaning up test database...")
            drop_db()

        def setUp(self):
            with get_db_session() as session:
                session.query(Review).delete()
                session.commit()
            
            self.test_review_data = {
                "client_id": self.client['id'],
                "service_id": self.service['id'],
                "rating": 5,
                "title": "Great service!",
                "body": "Really enjoyed working with this provider."
            }

        def test_create_review(self):
            review = self.review_service.create_review(**self.test_review_data)
            self.assertIsNotNone(review)
            self.assertEqual(review['rating'], self.test_review_data["rating"])
            self.assertEqual(review['title'], self.test_review_data["title"])

        def test_get_review(self):
            created = self.review_service.create_review(**self.test_review_data)
            fetched = self.review_service.get_review_by_id(created['id'])
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched['rating'], self.test_review_data["rating"])

        def test_update_review(self):
            review = self.review_service.create_review(**self.test_review_data)
            updated = self.review_service.update_review(
                review['id'],
                rating=4,
                title="Updated review"
            )
            self.assertEqual(updated['rating'], 4)
            self.assertEqual(updated['title'], "Updated review")

        def test_delete_review(self):
            review = self.review_service.create_review(**self.test_review_data)
            result = self.review_service.delete_review(review['id'])
            self.assertTrue(result)
            deleted = self.review_service.get_review_by_id(review['id'])
            self.assertIsNone(deleted)

        def test_get_average_rating(self):
            # Create a second client for testing multiple reviews
            second_client = self.account_service.create_account(
                username="client2",
                email="client2@example.com",
                password="testpass123"
            )

            # Create first review
            self.review_service.create_review(**self.test_review_data)  # rating: 5

            # Create second review from different client
            self.review_service.create_review(
                client_id=second_client['id'],  # Different client
                service_id=self.service['id'],
                rating=3,
                title="Another review",
                body="It was okay"
            )
            
            avg_service = self.review_service.get_average_rating(service_id=self.service['id'])
            self.assertEqual(avg_service, 4.0)  # (5 + 3) / 2 = 4.0

        def test_prevent_self_review(self):
            with self.assertRaises(ValueError):
                self.review_service.create_review(
                    client_id=self.provider['id'],  # Same as service provider
                    service_id=self.service['id'],
                    rating=5,
                    title="Self review",
                    body="Should not work"
                )

    unittest.main(verbosity=2)
