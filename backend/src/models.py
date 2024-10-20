from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Float, Boolean, ARRAY
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime, UTC

# Association table for the many-to-many relationship between Accounts and Hashtags
account_hashtags = Table('account_hashtags', Base.metadata,
    Column('account_id', Integer, ForeignKey('accounts.id'), primary_key=True),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id'), primary_key=True)
)

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    location = Column(ARRAY(Float), nullable=True)
    bio = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)

    # Relationships
    services = relationship("Service", back_populates="account")
    reviews = relationship("Review", back_populates="account", foreign_keys="[Review.account_id]")
    reviews_as_client = relationship("Review", back_populates="client", foreign_keys="[Review.client_id]")
    hashtags = relationship("Hashtag", secondary=account_hashtags, back_populates="accounts")

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Integer)  # Store price in cents
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="services")
    reviews = relationship("Review", back_populates="service")

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    rating = Column(Integer, nullable=False) # 1-5 stars
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="reviews", foreign_keys=[account_id])
    client = relationship("Account", back_populates="reviews_as_client", foreign_keys=[client_id])
    service = relationship("Service", back_populates="reviews")

class Hashtag(Base):
    __tablename__ = 'hashtags'

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    accounts = relationship("Account", secondary=account_hashtags, back_populates="hashtags")

if __name__ == "__main__":
    import unittest
    from db import get_db_session, init_db, drop_db

    class TestModels(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            init_db()

        @classmethod
        def tearDownClass(cls):
            drop_db()

        def setUp(self):
            self.db_context = get_db_session()
            self.session = self.db_context.__enter__()

        def tearDown(self):
            self.db_context.__exit__(None, None, None)

        def test_account_creation(self):
            account = Account(username="testuser", email="test@example.com", hashed_password="hashedpw")
            self.session.add(account)
            self.session.commit()

            fetched_account = self.session.query(Account).filter_by(username="testuser").first()
            self.assertIsNotNone(fetched_account)
            self.assertEqual(fetched_account.email, "test@example.com")

        def test_service_creation(self):
            account = Account(username="serviceuser", email="service@example.com", hashed_password="hashedpw")
            service = Service(title="Test Service", description="A test service", price=1000, account=account)
            self.session.add(account)
            self.session.add(service)
            self.session.commit()

            fetched_service = self.session.query(Service).filter_by(title="Test Service").first()
            self.assertIsNotNone(fetched_service)
            self.assertEqual(fetched_service.account.username, "serviceuser")

        def test_review_creation(self):
            account = Account(username="reviewer", email="reviewer@example.com", hashed_password="hashedpw")
            client = Account(username="client", email="client@example.com", hashed_password="hashedpw")
            service = Service(title="Reviewed Service", description="A service to be reviewed", price=2000, account=account)
            review = Review(account=account, client=client, service=service, rating=5, title="Great service", body="Highly recommended")
            
            self.session.add_all([account, client, service, review])
            self.session.commit()

            fetched_review = self.session.query(Review).filter_by(title="Great service").first()
            self.assertIsNotNone(fetched_review)
            self.assertEqual(fetched_review.rating, 5)
            self.assertEqual(fetched_review.account.username, "reviewer")
            self.assertEqual(fetched_review.client.username, "client")

        def test_hashtag_association(self):
            account = Account(username="hashtaguser", email="hashtag@example.com", hashed_password="hashedpw")
            hashtag1 = Hashtag(tag="python")
            hashtag2 = Hashtag(tag="sqlalchemy")
            account.hashtags.extend([hashtag1, hashtag2])
            
            self.session.add_all([account, hashtag1, hashtag2])
            self.session.commit()

            fetched_account = self.session.query(Account).filter_by(username="hashtaguser").first()
            self.assertEqual(len(fetched_account.hashtags), 2)
            self.assertIn("python", [h.tag for h in fetched_account.hashtags])
            self.assertIn("sqlalchemy", [h.tag for h in fetched_account.hashtags])

    unittest.main()
