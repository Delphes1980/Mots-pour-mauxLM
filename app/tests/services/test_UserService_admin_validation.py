import unittest
from app.tests.base_test import BaseTest
from app.services.UserService import UserService


class TestUserServiceAdminValidation(BaseTest):
    """Tests spécifiques pour la validation is_admin dans UserService"""

    def setUp(self):
        super().setUp()
        self.user_service = UserService()
        self.user_service.user_repository.db = self.db

    def test_create_user_admin_true(self):
        """Test création utilisateur avec is_admin=True"""
        user = self.user_service.create_user(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="Password123!",
            is_admin=True
        )
        
        self.assertTrue(user.is_admin)

    def test_create_user_admin_false(self):
        """Test création utilisateur avec is_admin=False"""
        user = self.user_service.create_user(
            first_name="Regular",
            last_name="User",
            email="regular@example.com",
            password="Password123!",
            is_admin=False
        )
        
        self.assertFalse(user.is_admin)

    def test_create_user_admin_none_defaults_to_false(self):
        """Test création utilisateur avec is_admin=None (doit être False par défaut)"""
        user = self.user_service.create_user(
            first_name="Default",
            last_name="User",
            email="default@example.com",
            password="Password123!",
            is_admin=None
        )
        
        self.assertFalse(user.is_admin)

    def test_create_user_admin_missing_defaults_to_false(self):
        """Test création utilisateur sans is_admin (doit être False par défaut)"""
        user = self.user_service.create_user(
            first_name="Missing",
            last_name="User",
            email="missing@example.com",
            password="Password123!"
            # is_admin non spécifié
        )
        
        self.assertFalse(user.is_admin)

    def test_update_user_promote_to_admin(self):
        """Test promotion d'un utilisateur normal en admin"""
        user = self.user_service.create_user(
            first_name="Regular",
            last_name="User",
            email="regular@example.com",
            password="Password123!",
            is_admin=False
        )
        
        updated_user = self.user_service.update_user(
            user.id,
            is_admin=True
        )
        
        self.assertTrue(updated_user.is_admin)

    def test_update_user_demote_from_admin(self):
        """Test rétrogradation d'un admin en utilisateur normal"""
        user = self.user_service.create_user(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="Password123!",
            is_admin=True
        )
        
        updated_user = self.user_service.update_user(
            user.id,
            is_admin=False
        )
        
        self.assertFalse(updated_user.is_admin)

    def test_update_user_admin_none_becomes_false(self):
        """Test mise à jour is_admin avec None (doit devenir False)"""
        user = self.user_service.create_user(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="Password123!",
            is_admin=True
        )
        
        updated_user = self.user_service.update_user(
            user.id,
            is_admin=None
        )
        
        self.assertFalse(updated_user.is_admin)

    def test_update_user_admin_with_other_fields(self):
        """Test mise à jour is_admin avec d'autres champs"""
        user = self.user_service.create_user(
            first_name="Regular",
            last_name="User",
            email="regular@example.com",
            password="Password123!",
            is_admin=False
        )
        
        updated_user = self.user_service.update_user(
            user.id,
            first_name="Admin",
            is_admin=True,
            address="123 Admin Street"
        )
        
        self.assertEqual(updated_user.first_name, "Admin")
        self.assertTrue(updated_user.is_admin)
        self.assertEqual(updated_user.address, "123 Admin Street")

    def test_create_user_admin_validation_type_error(self):
        """Test validation is_admin avec type invalide"""
        with self.assertRaises(TypeError):
            self.user_service.create_user(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                password="Password123!",
                is_admin="invalid_type"  # String au lieu de bool
            )

    def test_update_user_admin_validation_type_error(self):
        """Test validation is_admin avec type invalide lors de la mise à jour"""
        user = self.user_service.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        
        with self.assertRaises(TypeError):
            self.user_service.update_user(
                user.id,
                is_admin="invalid_type"  # String au lieu de bool
            )


if __name__ == '__main__':
    unittest.main()