import unittest
from flask_jwt_extended import decode_token
from app.tests.base_test import BaseTest
from app.services.AuthenticationService import AuthenticationService
from app.services.UserService import UserService


class TestAuthenticationServiceJWT(BaseTest):
    """Tests spécifiques pour la génération JWT dans AuthenticationService"""

    def setUp(self):
        super().setUp()
        self.auth_service = AuthenticationService()
        self.user_service = UserService()
        
        # Créer utilisateurs de test
        self.regular_user = self.user_service.create_user(
            first_name="Regular",
            last_name="User",
            email="regular@example.com",
            password="Password123!",
            is_admin=False
        )
        
        self.admin_user = self.user_service.create_user(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="AdminPass123!",
            is_admin=True
        )

    def test_login_returns_jwt_token(self):
        """Test que login retourne un token JWT valide"""
        token = self.auth_service.login("regular@example.com", "Password123!")
        
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
        
        # Vérifier que c'est un JWT valide
        decoded = decode_token(token)
        self.assertIn('sub', decoded)  # subject (user_id)
        self.assertIn('is_admin', decoded)  # custom claim

    def test_login_regular_user_jwt_claims(self):
        """Test claims JWT pour utilisateur normal"""
        token = self.auth_service.login("regular@example.com", "Password123!")
        
        decoded = decode_token(token)
        
        self.assertEqual(decoded['sub'], self.regular_user.id)
        self.assertFalse(decoded['is_admin'])

    def test_login_admin_user_jwt_claims(self):
        """Test claims JWT pour utilisateur admin"""
        token = self.auth_service.login("admin@example.com", "AdminPass123!")
        
        decoded = decode_token(token)
        
        self.assertEqual(decoded['sub'], self.admin_user.id)
        self.assertTrue(decoded['is_admin'])

    def test_login_invalid_credentials_no_token(self):
        """Test qu'aucun token n'est généré avec des credentials invalides"""
        with self.assertRaises(ValueError) as context:
            self.auth_service.login("regular@example.com", "WrongPassword!")
        
        self.assertIn("Invalid credentials", str(context.exception))

    def test_login_invalid_password_format_no_token(self):
        """Test qu'aucun token n'est généré avec un mot de passe mal formaté"""
        with self.assertRaises(ValueError) as context:
            self.auth_service.login("regular@example.com", "weak")
        
        self.assertEqual(str(context.exception), "Invalid credentials")

    def test_login_nonexistent_user_no_token(self):
        """Test qu'aucun token n'est généré pour utilisateur inexistant"""
        with self.assertRaises(ValueError) as context:
            self.auth_service.login("nonexistent@example.com", "Password123!")
        
        self.assertIn("Invalid credentials", str(context.exception))

    def test_jwt_token_contains_user_identity(self):
        """Test que le token JWT contient l'identité de l'utilisateur"""
        token = self.auth_service.login("regular@example.com", "Password123!")
        
        decoded = decode_token(token)
        
        # Vérifier que l'ID utilisateur est dans le token
        self.assertEqual(decoded['sub'], self.regular_user.id)
        
        # Vérifier que le token a une expiration
        self.assertIn('exp', decoded)

    def test_different_users_get_different_tokens(self):
        """Test que différents utilisateurs obtiennent des tokens différents"""
        token1 = self.auth_service.login("regular@example.com", "Password123!")
        token2 = self.auth_service.login("admin@example.com", "AdminPass123!")
        
        self.assertNotEqual(token1, token2)
        
        decoded1 = decode_token(token1)
        decoded2 = decode_token(token2)
        
        self.assertNotEqual(decoded1['sub'], decoded2['sub'])
        self.assertNotEqual(decoded1['is_admin'], decoded2['is_admin'])

    def test_admin_promotion_reflects_in_new_token(self):
        """Test que la promotion admin se reflète dans un nouveau token"""
        # Login initial (utilisateur normal)
        token1 = self.auth_service.login("regular@example.com", "Password123!")
        decoded1 = decode_token(token1)
        self.assertFalse(decoded1['is_admin'])
        
        # Promouvoir en admin
        self.user_service.update_user(self.regular_user.id, is_admin=True)
        
        # Nouveau login après promotion
        token2 = self.auth_service.login("regular@example.com", "Password123!")
        decoded2 = decode_token(token2)
        self.assertTrue(decoded2['is_admin'])

    def test_admin_demotion_reflects_in_new_token(self):
        """Test que la rétrogradation admin se reflète dans un nouveau token"""
        # Login initial (utilisateur admin)
        token1 = self.auth_service.login("admin@example.com", "AdminPass123!")
        decoded1 = decode_token(token1)
        self.assertTrue(decoded1['is_admin'])
        
        # Rétrograder en utilisateur normal
        self.user_service.update_user(self.admin_user.id, is_admin=False)
        
        # Nouveau login après rétrogradation
        token2 = self.auth_service.login("admin@example.com", "AdminPass123!")
        decoded2 = decode_token(token2)
        self.assertFalse(decoded2['is_admin'])


if __name__ == '__main__':
    unittest.main()