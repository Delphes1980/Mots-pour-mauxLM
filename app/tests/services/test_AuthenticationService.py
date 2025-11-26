import unittest
from app.tests.base_test import BaseTest
from app.services.AuthenticationService import AuthenticationService
from app.services.UserService import UserService
from app.utils import hash_password, verify_password


class TestAuthenticationService(BaseTest):

    def setUp(self):
        super().setUp()
        self.auth_service = AuthenticationService()
        self.user_service = UserService()

        # Créer un utilisateur de test
        self.test_user = self.user_service.create_user(
            first_name="John", 
            last_name="Doe", 
            email="john@example.com", 
            password="Password123!"
        )

    # Tests pour login()
    def test_login_success(self):
        """Test login avec des identifiants valides"""
        token = self.auth_service.login("john@example.com", "Password123!")
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_login_invalid_email_format(self):
        """Test login avec email invalide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.auth_service.login("invalid-email", "Password123!")
        self.assertIn("adresse e-mail invalide", str(context.exception).lower())

    def test_login_empty_email(self):
        """Test login avec email vide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.auth_service.login("", "Password123!")

    def test_login_invalid_password_format(self):
        """Test login avec mot de passe invalide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.auth_service.login("john@example.com", "weak")

    def test_login_empty_password(self):
        """Test login avec mot de passe vide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.auth_service.login("john@example.com", "")

    def test_login_user_not_found(self):
        """Test login avec email inexistant"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.auth_service.login("nonexistent@example.com", "Password123!")
        self.assertEqual(str(context.exception), "Invalid credentials")

    def test_login_wrong_password(self):
        """Test login avec mauvais mot de passe"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.auth_service.login("john@example.com", "WrongPassword123!")
        self.assertEqual(str(context.exception), "Invalid credentials")

    # Tests pour change_password()
    def test_change_password_success(self):
        """Test changement de mot de passe réussi"""
        updated_user = self.auth_service.change_password(
            self.test_user.id, "Password123!", "NewPassword456!"
        )

        # Vérifier que le mot de passe a été changé
        self.assertTrue(verify_password(updated_user.password, "NewPassword456!"))
        self.assertFalse(verify_password(updated_user.password, "Password123!"))

    def test_change_password_is_hashed(self):
        """Test que le nouveau mot de passe est bien hashé"""
        new_password = "NewPassword456!"
        
        updated_user = self.auth_service.change_password(
            self.test_user.id, "Password123!", new_password
        )

        # Vérifier que le mot de passe stocké n'est pas en clair
        self.assertNotEqual(updated_user.password, new_password)
        # Vérifier que c'est bien un hash bcrypt
        self.assertTrue(updated_user.password.startswith('$2b$'))
        # Vérifier que le hash fonctionne
        self.assertTrue(verify_password(updated_user.password, new_password))

    def test_change_password_invalid_user_id(self):
        """Test changement de mot de passe avec ID utilisateur invalide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.auth_service.change_password("invalid-id", "Password123!", "NewPassword456!")
        self.assertIn("user_id", str(context.exception))

    def test_change_password_user_not_found(self):
        """Test changement de mot de passe avec utilisateur inexistant"""
        from uuid import uuid4
        from app.utils import CustomError
        fake_id = str(uuid4())

        with self.assertRaises(CustomError) as context:
            self.auth_service.change_password(fake_id, "Password123!", "NewPassword456!")
        self.assertEqual(str(context.exception), "User not found")

    def test_change_password_invalid_old_password_format(self):
        """Test changement avec ancien mot de passe invalide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.auth_service.change_password(self.test_user.id, "weak", "NewPassword456!")

    def test_change_password_invalid_new_password_format(self):
        """Test changement avec nouveau mot de passe invalide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.auth_service.change_password(self.test_user.id, "Password123!", "weak")

    def test_change_password_wrong_old_password(self):
        """Test changement avec mauvais ancien mot de passe"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.auth_service.change_password(
                self.test_user.id, "WrongPassword123!", "NewPassword456!"
            )
        self.assertEqual(str(context.exception), "Invalid current password")

    def test_change_password_empty_old_password(self):
        """Test changement avec ancien mot de passe vide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.auth_service.change_password(self.test_user.id, "", "NewPassword456!")

    def test_change_password_empty_new_password(self):
        """Test changement avec nouveau mot de passe vide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.auth_service.change_password(self.test_user.id, "Password123!", "")

    def test_login_after_password_change(self):
        """Test login après changement de mot de passe"""
        # Changer le mot de passe
        self.auth_service.change_password(
            self.test_user.id, "Password123!", "NewPassword456!"
        )

        # Vérifier que l'ancien mot de passe ne fonctionne plus
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.auth_service.login("john@example.com", "Password123!")

        # Vérifier que le nouveau mot de passe fonctionne
        token = self.auth_service.login("john@example.com", "NewPassword456!")
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_hash_password_creates_different_hashes(self):
        """Test que hash_password génère des hashs différents pour le même mot de passe"""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Les hashs doivent être différents (salt aléatoire)
        self.assertNotEqual(hash1, hash2)
        # Mais les deux doivent être vérifiables
        self.assertTrue(verify_password(hash1, password))
        self.assertTrue(verify_password(hash2, password))

    def test_hash_password_format(self):
        """Test que hash_password génère un hash bcrypt valide"""
        password = "TestPassword123!"
        hashed = hash_password(password)

        # Vérifier le format bcrypt
        self.assertTrue(hashed.startswith('$2b$'))
        self.assertTrue(len(hashed) == 60)  # Longueur standard bcrypt

    def test_verify_password_with_manual_hash(self):
        """Test verify_password avec un hash créé manuellement"""
        password = "ManualTest123!"
        hashed = hash_password(password)

        # Vérification positive
        self.assertTrue(verify_password(hashed, password))
        # Vérification négative
        self.assertFalse(verify_password(hashed, "WrongPassword123!"))


if __name__ == '__main__':
    unittest.main()