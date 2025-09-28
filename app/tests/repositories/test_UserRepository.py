import unittest
from sqlalchemy.exc import SQLAlchemyError
from app.tests.base_test import BaseTest
from app.models.user import User
from app.persistence.UserRepository import UserRepository


class TestUserRepository(BaseTest):
    def setUp(self):
        super().setUp()
        self.user_repo = UserRepository()
        # Forcer l'utilisation de l'instance DB de test
        self.user_repo.db = self.db

    def test_create_user_success(self):
        """Test création utilisateur réussie"""
        user = self.user_repo.create_user(
            first_name="John",
            last_name="Doe", 
            email="john@example.com",
            password="Password123!",
            address="123 Main St",
            phone_number="0123456789"
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "john@example.com")
        self.assertEqual(user.address, "123 Main St")
        self.assertEqual(user.phone_number, "0123456789")
        self.assertFalse(user.is_admin)

    def test_create_user_with_admin_flag(self):
        """Test création utilisateur admin"""
        user = self.user_repo.create_user(
            first_name="Admin",
            last_name="User",
            email="admin@example.com", 
            password="Password123!",
            is_admin=True
        )
        
        self.assertTrue(user.is_admin)

    def test_create_user_duplicate_email(self):
        """Test création utilisateur avec email existant"""
        # Créer premier utilisateur
        self.user_repo.create_user(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="Password123!"
        )
        
        # Tenter de créer un autre avec même email
        with self.assertRaises(ValueError) as context:
            self.user_repo.create_user(
                first_name="Jane",
                last_name="Smith", 
                email="john@example.com",
                password="Password456!"
            )
        
        self.assertIn("Un utilisateur avec cet email existe déjà", str(context.exception))

    def test_get_by_email_existing_user(self):
        """Test récupération utilisateur par email existant"""
        # Créer utilisateur
        created_user = self.user_repo.create_user(
            first_name="John",
            last_name="Doe",
            email="john@example.com", 
            password="Password123!"
        )
        
        # Récupérer par email
        found_user = self.user_repo.get_by_email("john@example.com")
        
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.id, created_user.id)
        self.assertEqual(found_user.email, "john@example.com")

    def test_get_by_email_non_existing_user(self):
        """Test récupération utilisateur par email inexistant"""
        user = self.user_repo.get_by_email("nonexistent@example.com")
        self.assertIsNone(user)

    def test_create_user_minimal_data(self):
        """Test création utilisateur avec données minimales"""
        user = self.user_repo.create_user(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="Password123!"
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Smith") 
        self.assertEqual(user.email, "jane@example.com")
        self.assertIsNone(user.address)
        self.assertIsNone(user.phone_number)
        self.assertFalse(user.is_admin)

    def test_inheritance_from_base_repository(self):
        """Test que UserRepository hérite bien de BaseRepository"""
        # Test méthodes héritées avec create
        user = self.user_repo.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!",
            address=None,
            phone_number=None
        )
        self.assertIsNotNone(user.id)
        
        # Test get_by_id (méthode héritée)
        found_user = self.user_repo.get_by_id(user.id)
        self.assertEqual(found_user.id, user.id)
        
        # Test get_all (méthode héritée)
        all_users = self.user_repo.get_all()
        self.assertIn(user, all_users)

    def test_model_class_consistency(self):
        """Test que model_class est bien configuré"""
        self.assertEqual(self.user_repo.model_class, User)


if __name__ == "__main__":
    unittest.main()