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
    reviews = relationship("Review", back_populates="account")
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
    rating = Column(Integer, nullable=False) # 1-5 stars
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="reviews")
    service = relationship("Service", back_populates="reviews")

class Hashtag(Base):
    __tablename__ = 'hashtags'

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    accounts = relationship("Account", secondary=account_hashtags, back_populates="hashtags")
