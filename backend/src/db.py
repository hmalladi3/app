from typing import List, Dict, Any, Optional, Callable, Generator
from uuid import UUID
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Database configuration
DB_NAME = os.getenv("DB_NAME", "testdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Create the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        logger.info("Database session started")
        yield session
        session.commit()
        logger.info("Database session committed")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error occurred: {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise
    finally:
        session.close()
        logger.info("Database session closed")

def init_db():
    """Initialize the database."""
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all tables in the database."""
    Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    print("Testing database operations...")

    # Function to reset the database
    def reset_db():
        print("Resetting database...")
        drop_db()
        init_db()

    # Test database connection
    def test_db_connection():
        print("Testing database connection...")
        try:
            with get_db_session() as session:
                session.execute(text("SELECT 1"))
            print("Database connection successful")
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            raise

    # Test creating a table and inserting data
    def test_create_and_insert():
        print("Testing create table and insert operations...")
        try:
            with get_db_session() as session:
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) NOT NULL
                    )
                """))
                session.execute(text("INSERT INTO test_table (name) VALUES ('Test Name')"))
                result = session.execute(text("SELECT * FROM test_table")).fetchone()
                assert result[1] == 'Test Name', "Inserted data doesn't match"
            print("Create table and insert operations successful")
        except Exception as e:
            print(f"Create table and insert operations failed: {str(e)}")
            raise

    # Test querying data
    def test_query():
        print("Testing query operation...")
        try:
            with get_db_session() as session:
                result = session.execute(text("SELECT name FROM test_table WHERE id = 1")).fetchone()
                assert result[0] == 'Test Name', "Queried data doesn't match"
            print("Query operation successful")
        except Exception as e:
            print(f"Query operation failed: {str(e)}")
            raise

    # Test updating data
    def test_update():
        print("Testing update operation...")
        try:
            with get_db_session() as session:
                session.execute(text("UPDATE test_table SET name = 'Updated Name' WHERE id = 1"))
                result = session.execute(text("SELECT name FROM test_table WHERE id = 1")).fetchone()
                assert result[0] == 'Updated Name', "Updated data doesn't match"
            print("Update operation successful")
        except Exception as e:
            print(f"Update operation failed: {str(e)}")
            raise

    # Test deleting data
    def test_delete():
        print("Testing delete operation...")
        try:
            with get_db_session() as session:
                session.execute(text("DELETE FROM test_table WHERE id = 1"))
                result = session.execute(text("SELECT * FROM test_table")).fetchall()
                assert len(result) == 0, "Delete operation didn't remove all rows"
            print("Delete operation successful")
        except Exception as e:
            print(f"Delete operation failed: {str(e)}")
            raise

    # Run tests
    try:
        reset_db()
        test_db_connection()
        test_create_and_insert()
        test_query()
        test_update()
        test_delete()
        print("All tests passed successfully!")
    except Exception as e:
        print(f"Tests failed: {str(e)}")
    finally:
        reset_db()
        print("Database reset to original state.")
