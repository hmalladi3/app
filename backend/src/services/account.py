from db import get_db_session
from models import Account
from sqlalchemy.exc import IntegrityError
from argon2 import PasswordHasher, exceptions

ph = PasswordHasher()

class AccountService:
    def __init__(self):
        pass

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
                session.refresh(newAcct)
                return newAcct
            except IntegrityError:
                session.rollback()
                raise ValueError("An error occurred while creating the account")

    def get_account_by_id(self, id: int):
        with get_db_session() as session:
            return session.query(Account).filter(Account.id == id).first()

    def get_account_by_username(self, username: str):
        with get_db_session() as session:
            return session.query(Account).filter(Account.username == username).first()

    def get_account_by_email(self, email: str):
        with get_db_session() as session:
            return session.query(Account).filter(Account.email == email).first()

    def update_account(self, id: int, username: str = None, email: str = None, password: str = None):
        with get_db_session() as session:
            account = session.query(Account).filter(Account.id == id).first()
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
                session.refresh(account)
                return account
            except IntegrityError:
                session.rollback()
                raise ValueError("An error occurred while updating the account")

    def delete_account(self, id: int):
        with get_db_session() as session:
            account = session.query(Account).filter(Account.id == id).first()
            if account:
                session.delete(account)
                session.commit()
                return True
            return False

    def login(self, username_or_email: str, password: str):
        with get_db_session() as session:
            # Try to find the account by username or email
            account = session.query(Account).filter(
                (Account.username == username_or_email) | (Account.email == username_or_email)
            ).first()

            if not account:
                raise ValueError("Invalid username or email")

            if self.verify_password(account, password):
                return account
            else:
                raise ValueError("Invalid password")

    def verify_password(self, account: Account, password: str) -> bool:
        try:
            ph.verify(account.hashed_password, password)
            return True
        except exceptions.VerifyMismatchError:
            return False
