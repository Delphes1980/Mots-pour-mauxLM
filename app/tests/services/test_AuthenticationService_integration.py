import unittest
from app.tests.base_test import BaseTest
from app.services.AuthenticationService import AuthenticationService
from app.services.UserService import UserService
from app.utils import verify_password


class TestAuthenticationServiceIntegration(BaseTest):
    """Tests d'intégration pour AuthenticationService avec vraie base de données"""

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

    def test_full_authentication_workflow(self):
        """Test workflow complet d'authentification"""
        # Test login initial (retourne un token, pas un user)
        token = self.auth_service.login("john@example.com", "Password123!")
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
        
        # Test changement de mot de passe
        updated_user = self.auth_service.change_password(
            self.test_user.id, "Password123!", "NewPassword456!"
        )
        
        # Vérifier que le nouveau mot de passe est hashé
        self.assertTrue(verify_password(updated_user.password, "NewPassword456!"))
        self.assertFalse(verify_password(updated_user.password, "Password123!"))
        
        # Test login avec nouveau mot de passe
        new_token = self.auth_service.login("john@example.com", "NewPassword456!")
        self.assertIsInstance(new_token, str)
        self.assertTrue(len(new_token) > 0)
        
        # Vérifier que l'ancien mot de passe ne fonctionne plus
        with self.assertRaises(ValueError) as context:
            self.auth_service.login("john@example.com", "Password123!")
        self.assertEqual(str(context.exception), "Invalid credentials")

    def test_multiple_password_changes(self):
        """Test changements multiples de mot de passe"""
        passwords = ["NewPass1!", "NewPass2!", "NewPass3!"]
        current_password = "Password123!"
        
        for new_password in passwords:
            # Changer le mot de passe
            updated_user = self.auth_service.change_password(
                self.test_user.id, current_password, new_password
            )
            
            # Vérifier que le nouveau mot de passe fonctionne
            token = self.auth_service.login("john@example.com", new_password)
            self.assertIsInstance(token, str)
            
            # Vérifier que l'ancien ne fonctionne plus
            with self.assertRaises(ValueError):
                self.auth_service.login("john@example.com", current_password)
            
            current_password = new_password

    def test_concurrent_user_authentication(self):
        """Test authentification avec plusieurs utilisateurs"""
        # Créer second utilisateur
        user2 = self.user_service.create_user(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="JanePassword123!"
        )
        
        # Test login des deux utilisateurs
        token1 = self.auth_service.login("john@example.com", "Password123!")
        token2 = self.auth_service.login("jane@example.com", "JanePassword123!")
        
        self.assertIsInstance(token1, str)
        self.assertIsInstance(token2, str)
        self.assertNotEqual(token1, token2)
        
        # Changer mot de passe du premier utilisateur
        self.auth_service.change_password(
            self.test_user.id, "Password123!", "JohnNewPass123!"
        )
        
        # Vérifier que le second utilisateur peut toujours se connecter
        token2_still = self.auth_service.login("jane@example.com", "JanePassword123!")
        self.assertIsInstance(token2_still, str)
        
        # Vérifier que le premier utilisateur utilise le nouveau mot de passe
        token1_new = self.auth_service.login("john@example.com", "JohnNewPass123!")
        self.assertIsInstance(token1_new, str)

    def test_password_security_persistence(self):
        """Test sécurité et persistance des mots de passe"""
        original_password_hash = self.test_user.password
        
        # Changer le mot de passe
        updated_user = self.auth_service.change_password(
            self.test_user.id, "Password123!", "SuperSecure789!"
        )
        
        # Vérifier que le hash a changé
        self.assertNotEqual(updated_user.password, original_password_hash)
        
        # Vérifier que le mot de passe n'est pas stocké en clair
        self.assertNotEqual(updated_user.password, "SuperSecure789!")
        
        # Vérifier que le hash est au format bcrypt
        self.assertTrue(updated_user.password.startswith('$2b$'))
        
        # Récupérer l'utilisateur depuis la base pour vérifier la persistance
        fresh_user = self.user_service.get_user_by_id(self.test_user.id)
        self.assertEqual(fresh_user.password, updated_user.password)
        
        # Vérifier que le login fonctionne avec les données persistées
        token = self.auth_service.login("john@example.com", "SuperSecure789!")
        self.assertIsInstance(token, str)


if __name__ == '__main__':
    unittest.main()