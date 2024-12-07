import sys
from pathlib import Path

# Add the project root directory to sys.path
project_root = Path(__file__).resolve().parents[2]  # This should be the 'backend' directory
sys.path.append(str(project_root))

# Now you can import from src.db and src.models
from src.db import get_db_session, init_db, drop_db
from src.models import Account

from sqlalchemy.exc import IntegrityError
from argon2 import PasswordHasher, exceptions

ph = PasswordHasher()

class AccountService:
    def create_account(self, username: str, email: str, password: str):
        with get_db_session() as session:
            # Check if username or email already exists
            existing_user = session.query(Account).filter(
                (Account.username == username) | (Account.email == email)
            ).first()
            
            if existing_user:
                if existing_user.username == username:
                    raise ValueError("Username already exists")
                else:
                    raise ValueError("Email already exists")
            
            hashed_password = ph.hash(password)
            newAcct = Account(username=username, email=email, hashed_password=hashed_password)
            session.add(newAcct)
            try:
                session.commit()
                return {
                    'id': newAcct.id,
                    'username': newAcct.username,
                    'email': newAcct.email
                }
            except IntegrityError:
                session.rollback()
                raise ValueError("An error occurred while creating the account")

    def get_account_by_id(self, id: int):
        with get_db_session() as session:
            account = session.get(Account, id)
            if account:
                return {
                    'id': account.id,
                    'username': account.username,
                    'email': account.email
                }
            return None

    def get_account_by_username(self, username: str):
        with get_db_session() as session:
            account = session.query(Account).filter(Account.username == username).first()
            if account:
                return {
                    'id': account.id,
                    'username': account.username,
                    'email': account.email
                }
            return None

    def get_account_by_email(self, email: str):
        with get_db_session() as session:
            account = session.query(Account).filter(Account.email == email).first()
            if account:
                return {
                    'id': account.id,
                    'username': account.username,
                    'email': account.email
                }
            return None

    def update_account(self, id: int, username: str = None, email: str = None, password: str = None):
        with get_db_session() as session:
            account = session.get(Account, id)
            if not account:
                raise ValueError("Account not found")

            if username and username != account.username:
                existing = session.query(Account).filter(Account.username == username).first()
                if existing:
                    raise ValueError("Username already exists")
                account.username = username

            if email and email != account.email:
                existing = session.query(Account).filter(Account.email == email).first()
                if existing:
                    raise ValueError("Email already exists")
                account.email = email

            if password:
                account.hashed_password = ph.hash(password)

            try:
                session.commit()
                return {
                    'id': account.id,
                    'username': account.username,
                    'email': account.email
                }
            except IntegrityError:
                session.rollback()
                raise ValueError("An error occurred while updating the account")

    def delete_account(self, id: int):
        with get_db_session() as session:
            account = session.get(Account, id)
            if account:
                session.delete(account)
                session.commit()
                return True
            return False

    def login(self, username_or_email: str, password: str):
        with get_db_session() as session:
            account = session.query(Account).filter(
                (Account.username == username_or_email) | (Account.email == username_or_email)
            ).first()

            if not account:
                raise ValueError("Invalid username or email")

            if self.verify_password(account, password):
                return {
                    'id': account.id,
                    'username': account.username,
                    'email': account.email
                }
            else:
                raise ValueError("Invalid password")

    def verify_password(self, account: Account, password: str) -> bool:
        try:
            ph.verify(account.hashed_password, password)
            return True
        except exceptions.VerifyMismatchError:
            return False

if __name__ == "__main__":
    import unittest

    class TestAccountService(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            print("Initializing test database...")
            init_db()
            cls.account_service = AccountService()

        @classmethod
        def tearDownClass(cls):
            print("Cleaning up test database...")
            drop_db()

        def setUp(self):
            with get_db_session() as session:
                session.query(Account).delete()
                session.commit()
            
            self.test_account_data = {
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "testpassword123"
            }

        def test_create_account(self):
            account = self.account_service.create_account(**self.test_account_data)
            self.assertIsNotNone(account)
            self.assertEqual(account['username'], self.test_account_data["username"])
            self.assertEqual(account['email'], self.test_account_data["email"])

        def test_get_account(self):
            created = self.account_service.create_account(**self.test_account_data)
            fetched = self.account_service.get_account_by_id(created['id'])
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched['username'], self.test_account_data["username"])

        def test_update_account(self):
            account = self.account_service.create_account(**self.test_account_data)
            updated_data = {"username": "updateduser", "email": "updated@example.com"}
            updated = self.account_service.update_account(account['id'], **updated_data)
            self.assertEqual(updated['username'], updated_data["username"])
            self.assertEqual(updated['email'], updated_data["email"])

        def test_delete_account(self):
            account = self.account_service.create_account(**self.test_account_data)
            result = self.account_service.delete_account(account['id'])
            self.assertTrue(result)
            deleted = self.account_service.get_account_by_id(account['id'])
            self.assertIsNone(deleted)

        def test_login(self):
            self.account_service.create_account(**self.test_account_data)
            logged_in = self.account_service.login(
                self.test_account_data["username"], 
                self.test_account_data["password"]
            )
            self.assertIsNotNone(logged_in)
            self.assertEqual(logged_in['username'], self.test_account_data["username"])

        def test_verify_password(self):
            created = self.account_service.create_account(**self.test_account_data)
            with get_db_session() as session:
                account = session.get(Account, created['id'])
                self.assertTrue(
                    self.account_service.verify_password(
                        account, 
                        self.test_account_data["password"]
                    )
                )
                self.assertFalse(
                    self.account_service.verify_password(
                        account, 
                        "wrongpassword"
                    )
                )

    unittest.main(verbosity=2)
