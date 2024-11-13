import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.db import get_db_session
from src.models import Service, Account
from sqlalchemy.exc import IntegrityError

class ServiceService:
    def create_service(self, account_id: int, title: str, description: str, price: int):
        """Create a new service. Price should be in cents (e.g., $10.00 = 1000)."""
        with get_db_session() as session:
            # Verify account exists
            account = session.get(Account, account_id)
            if not account:
                raise ValueError("Account not found")
            
            service = Service(
                account_id=account_id,
                title=title,
                description=description,
                price=price
            )
            session.add(service)
            
            try:
                session.commit()
                return {
                    'id': service.id,
                    'account_id': service.account_id,
                    'title': service.title,
                    'description': service.description,
                    'price': service.price,
                    'created_at': service.created_at,
                    'updated_at': service.updated_at
                }
            except IntegrityError:
                session.rollback()
                raise ValueError("An error occurred while creating the service")

    def get_service_by_id(self, service_id: int):
        with get_db_session() as session:
            service = session.get(Service, service_id)
            if service:
                return {
                    'id': service.id,
                    'account_id': service.account_id,
                    'title': service.title,
                    'description': service.description,
                    'price': service.price,
                    'created_at': service.created_at,
                    'updated_at': service.updated_at
                }
            return None

    def get_services_by_account(self, account_id: int):
        with get_db_session() as session:
            services = session.query(Service).filter(Service.account_id == account_id).all()
            return [{
                'id': service.id,
                'account_id': service.account_id,
                'title': service.title,
                'description': service.description,
                'price': service.price,
                'created_at': service.created_at,
                'updated_at': service.updated_at
            } for service in services]

    def update_service(self, service_id: int, title: str = None, description: str = None, price: int = None):
        with get_db_session() as session:
            service = session.get(Service, service_id)
            if not service:
                raise ValueError("Service not found")

            if title is not None:
                service.title = title
            if description is not None:
                service.description = description
            if price is not None:
                service.price = price

            try:
                session.commit()
                return {
                    'id': service.id,
                    'account_id': service.account_id,
                    'title': service.title,
                    'description': service.description,
                    'price': service.price,
                    'created_at': service.created_at,
                    'updated_at': service.updated_at
                }
            except IntegrityError:
                session.rollback()
                raise ValueError("An error occurred while updating the service")

    def delete_service(self, service_id: int):
        with get_db_session() as session:
            service = session.get(Service, service_id)
            if service:
                session.delete(service)
                session.commit()
                return True
            return False

    def search_services(self, keyword: str = None, min_price: int = None, max_price: int = None):
        with get_db_session() as session:
            query = session.query(Service)
            
            if keyword:
                query = query.filter(
                    (Service.title.ilike(f'%{keyword}%')) |
                    (Service.description.ilike(f'%{keyword}%'))
                )
            
            if min_price is not None:
                query = query.filter(Service.price >= min_price)
            
            if max_price is not None:
                query = query.filter(Service.price <= max_price)
            
            services = query.all()
            return [{
                'id': service.id,
                'account_id': service.account_id,
                'title': service.title,
                'description': service.description,
                'price': service.price,
                'created_at': service.created_at,
                'updated_at': service.updated_at
            } for service in services]


if __name__ == "__main__":
    import unittest
    from src.db import init_db, drop_db

    class TestServiceService(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            print("Initializing test database...")
            init_db()
            cls.service_service = ServiceService()
            
            # Create a test account
            from src.services.account import AccountService
            cls.account_service = AccountService()
            cls.test_account = cls.account_service.create_account(
                username="testbusiness",
                email="business@example.com",
                password="testpass123"
            )

        @classmethod
        def tearDownClass(cls):
            print("Cleaning up test database...")
            drop_db()

        def setUp(self):
            with get_db_session() as session:
                session.query(Service).delete()
                session.commit()
            
            self.test_service_data = {
                "account_id": self.test_account['id'],
                "title": "Test Service",
                "description": "A test service description",
                "price": 1000  # $10.00
            }

        def test_create_service(self):
            service = self.service_service.create_service(**self.test_service_data)
            self.assertIsNotNone(service)
            self.assertEqual(service['title'], self.test_service_data["title"])
            self.assertEqual(service['price'], self.test_service_data["price"])

        def test_get_service(self):
            created = self.service_service.create_service(**self.test_service_data)
            fetched = self.service_service.get_service_by_id(created['id'])
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched['title'], self.test_service_data["title"])

        def test_get_services_by_account(self):
            self.service_service.create_service(**self.test_service_data)
            services = self.service_service.get_services_by_account(self.test_account['id'])
            self.assertEqual(len(services), 1)
            self.assertEqual(services[0]['title'], self.test_service_data["title"])

        def test_update_service(self):
            service = self.service_service.create_service(**self.test_service_data)
            updated_data = {"title": "Updated Service", "price": 2000}
            updated = self.service_service.update_service(service['id'], **updated_data)
            self.assertEqual(updated['title'], updated_data["title"])
            self.assertEqual(updated['price'], updated_data["price"])

        def test_delete_service(self):
            service = self.service_service.create_service(**self.test_service_data)
            result = self.service_service.delete_service(service['id'])
            self.assertTrue(result)
            deleted = self.service_service.get_service_by_id(service['id'])
            self.assertIsNone(deleted)

        def test_search_services(self):
            # Create multiple services
            self.service_service.create_service(**self.test_service_data)
            self.service_service.create_service(
                account_id=self.test_account['id'],
                title="Premium Service",
                description="An expensive service",
                price=5000
            )

            # Test keyword search
            results = self.service_service.search_services(keyword="Premium")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['title'], "Premium Service")

            # Test price range search
            results = self.service_service.search_services(min_price=2000)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['price'], 5000)

    unittest.main(verbosity=2)
