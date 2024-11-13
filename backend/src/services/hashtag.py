import sys
from pathlib import Path
from sqlalchemy import text

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.db import get_db_session
from src.models import Hashtag, Account
from sqlalchemy.exc import IntegrityError
from typing import List

class HashtagService:
    def create_hashtag(self, tag: str):
        """Create a new hashtag if it doesn't exist"""
        # Normalize the tag (lowercase, remove #)
        tag = self._normalize_tag(tag)
        
        with get_db_session() as session:
            existing = session.query(Hashtag).filter(Hashtag.tag == tag).first()
            if existing:
                return {
                    'id': existing.id,
                    'tag': existing.tag,
                    'created_at': existing.created_at
                }
            
            hashtag = Hashtag(tag=tag)
            session.add(hashtag)
            try:
                session.commit()
                return {
                    'id': hashtag.id,
                    'tag': hashtag.tag,
                    'created_at': hashtag.created_at
                }
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Error creating hashtag: {tag}")

    def get_hashtag(self, tag: str):
        """Get a hashtag by its tag string"""
        tag = self._normalize_tag(tag)
        with get_db_session() as session:
            hashtag = session.query(Hashtag).filter(Hashtag.tag == tag).first()
            if hashtag:
                return {
                    'id': hashtag.id,
                    'tag': hashtag.tag,
                    'created_at': hashtag.created_at
                }
            return None

    def get_hashtag_by_id(self, hashtag_id: int):
        """Get a hashtag by its ID"""
        with get_db_session() as session:
            hashtag = session.get(Hashtag, hashtag_id)
            if hashtag:
                return {
                    'id': hashtag.id,
                    'tag': hashtag.tag,
                    'created_at': hashtag.created_at
                }
            return None

    def add_hashtags_to_account(self, account_id: int, tags: List[str]):
        """Add multiple hashtags to an account"""
        with get_db_session() as session:
            account = session.get(Account, account_id)
            if not account:
                raise ValueError("Account not found")

            added_tags = []
            for tag in tags:
                tag = self._normalize_tag(tag)
                # Get or create hashtag
                hashtag = session.query(Hashtag).filter(Hashtag.tag == tag).first()
                if not hashtag:
                    hashtag = Hashtag(tag=tag)
                    session.add(hashtag)
                
                if hashtag not in account.hashtags:
                    account.hashtags.append(hashtag)
                    added_tags.append(tag)

            try:
                session.commit()
                return added_tags
            except IntegrityError:
                session.rollback()
                raise ValueError("Error adding hashtags to account")

    def remove_hashtag_from_account(self, account_id: int, tag: str):
        """Remove a hashtag from an account"""
        tag = self._normalize_tag(tag)
        with get_db_session() as session:
            account = session.get(Account, account_id)
            if not account:
                raise ValueError("Account not found")

            hashtag = session.query(Hashtag).filter(Hashtag.tag == tag).first()
            if not hashtag:
                return False

            if hashtag in account.hashtags:
                account.hashtags.remove(hashtag)
                session.commit()
                return True
            return False

    def get_account_hashtags(self, account_id: int):
        """Get all hashtags for an account"""
        with get_db_session() as session:
            account = session.get(Account, account_id)
            if not account:
                raise ValueError("Account not found")
            
            return [{
                'id': tag.id,
                'tag': tag.tag,
                'created_at': tag.created_at
            } for tag in account.hashtags]

    def get_accounts_by_hashtag(self, tag: str):
        """Get all accounts that have a specific hashtag"""
        tag = self._normalize_tag(tag)
        with get_db_session() as session:
            hashtag = session.query(Hashtag).filter(Hashtag.tag == tag).first()
            if not hashtag:
                return []
            
            return [{
                'id': account.id,
                'username': account.username,
                'email': account.email
            } for account in hashtag.accounts]

    def search_hashtags(self, query: str):
        """Search hashtags by partial match"""
        query = self._normalize_tag(query)
        with get_db_session() as session:
            hashtags = session.query(Hashtag).filter(
                Hashtag.tag.ilike(f'%{query}%')
            ).all()
            
            return [{
                'id': tag.id,
                'tag': tag.tag,
                'created_at': tag.created_at
            } for tag in hashtags]

    def _normalize_tag(self, tag: str) -> str:
        """Normalize hashtag format (lowercase, remove #)"""
        tag = tag.lower().strip()
        return tag.lstrip('#')


if __name__ == "__main__":
    import unittest
    from src.db import init_db, drop_db
    from src.services.account import AccountService

    class TestHashtagService(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            print("Initializing test database...")
            init_db()
            cls.hashtag_service = HashtagService()
            cls.account_service = AccountService()

        @classmethod
        def tearDownClass(cls):
            print("Cleaning up test database...")
            drop_db()

        def setUp(self):
            """Clear all test data before each test"""
            with get_db_session() as session:
                # First clear the association table using proper text() wrapper
                session.execute(text('DELETE FROM account_hashtags'))
                # Then clear the main tables
                session.query(Hashtag).delete()
                session.query(Account).delete()
                session.commit()

            # Create test account after cleanup
            self.test_account = self.account_service.create_account(
                username="testuser",
                email="test@example.com",
                password="testpass123"
            )

        def test_create_hashtag(self):
            hashtag = self.hashtag_service.create_hashtag("python")
            self.assertIsNotNone(hashtag)
            self.assertEqual(hashtag['tag'], "python")

        def test_normalize_hashtag(self):
            # Should handle different formats
            hashtag1 = self.hashtag_service.create_hashtag("Python")
            hashtag2 = self.hashtag_service.create_hashtag("#python")
            self.assertEqual(hashtag1['id'], hashtag2['id'])  # Same hashtag

        def test_add_hashtags_to_account(self):
            tags = ["python", "coding", "developer"]
            added = self.hashtag_service.add_hashtags_to_account(
                self.test_account['id'], 
                tags
            )
            self.assertEqual(len(added), 3)
            
            # Verify hashtags were added
            account_tags = self.hashtag_service.get_account_hashtags(
                self.test_account['id']
            )
            self.assertEqual(len(account_tags), 3)

        def test_remove_hashtag(self):
            # Add hashtags first
            self.hashtag_service.add_hashtags_to_account(
                self.test_account['id'], 
                ["python", "coding"]
            )
            
            # Remove one hashtag
            result = self.hashtag_service.remove_hashtag_from_account(
                self.test_account['id'], 
                "python"
            )
            self.assertTrue(result)
            
            # Verify removal
            tags = self.hashtag_service.get_account_hashtags(self.test_account['id'])
            self.assertEqual(len(tags), 1)
            self.assertEqual(tags[0]['tag'], "coding")

        def test_get_accounts_by_hashtag(self):
            # Create another account
            account2 = self.account_service.create_account(
                username="another",
                email="another@example.com",
                password="testpass123"
            )
            
            # Add same hashtag to both accounts
            self.hashtag_service.add_hashtags_to_account(
                self.test_account['id'], 
                ["python"]
            )
            self.hashtag_service.add_hashtags_to_account(
                account2['id'], 
                ["python"]
            )
            
            # Get accounts with #python
            accounts = self.hashtag_service.get_accounts_by_hashtag("python")
            self.assertEqual(len(accounts), 2)

        def test_search_hashtags(self):
            # Create some hashtags
            self.hashtag_service.create_hashtag("python")
            self.hashtag_service.create_hashtag("pythonista")
            self.hashtag_service.create_hashtag("coding")
            
            # Search for python-related tags
            results = self.hashtag_service.search_hashtags("python")
            self.assertEqual(len(results), 2)  # should find "python" and "pythonista"

    unittest.main(verbosity=2)
