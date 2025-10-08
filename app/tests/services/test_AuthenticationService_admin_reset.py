#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.services.AuthenticationService import AuthenticationService
from app.services.UserService import UserService
from app.utils import verify_password, CustomError


class TestAuthenticationServiceAdminReset(BaseTest):
    """Tests pour la méthode admin_reset_password d'AuthenticationService"""

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

    def test_admin_reset_password_success(self):
        """Test réinitialisation réussie du mot de passe par admin"""
        new_password = "AdminReset456!"
        
        updated_user = self.auth_service.admin_reset_password(
            self.test_user.id, new_password
        )

        # Vérifier que le mot de passe a été changé
        self.assertTrue(verify_password(updated_user.password, new_password))
        self.assertFalse(verify_password(updated_user.password, "Password123!"))

    def test_admin_reset_password_is_hashed(self):
        """Test que le nouveau mot de passe est bien hashé"""
        new_password = "AdminReset456!"
        
        updated_user = self.auth_service.admin_reset_password(
            self.test_user.id, new_password
        )

        # Vérifier que le mot de passe stocké n'est pas en clair
        self.assertNotEqual(updated_user.password, new_password)
        # Vérifier que c'est bien un hash bcrypt
        self.assertTrue(updated_user.password.startswith('$2b$'))
        # Vérifier que le hash fonctionne
        self.assertTrue(verify_password(updated_user.password, new_password))

    def test_admin_reset_password_invalid_user_id(self):
        """Test réinitialisation avec ID utilisateur invalide"""
        with self.assertRaises(CustomError) as context:
            self.auth_service.admin_reset_password("invalid-id", "AdminReset456!")
        self.assertIn("user_id", str(context.exception))

    def test_admin_reset_password_user_not_found(self):
        """Test réinitialisation avec utilisateur inexistant"""
        from uuid import uuid4
        fake_id = str(uuid4())

        with self.assertRaises(CustomError) as context:
            self.auth_service.admin_reset_password(fake_id, "AdminReset456!")
        self.assertEqual(str(context.exception), "User not found")

    def test_admin_reset_password_invalid_new_password_format(self):
        """Test réinitialisation avec nouveau mot de passe invalide"""
        invalid_passwords = [
            "weak",  # Trop court, pas de majuscule, pas de caractère spécial
            "WeakPassword",  # Pas de chiffre, pas de caractère spécial
            "weakpassword123",  # Pas de majuscule, pas de caractère spécial
            "WeakPassword123",  # Pas de caractère spécial
            "Weak123",  # Pas de caractère spécial
            "",  # Vide
        ]
        
        for invalid_password in invalid_passwords:
            with self.subTest(password=invalid_password):
                with self.assertRaises(CustomError):
                    self.auth_service.admin_reset_password(self.test_user.id, invalid_password)

    def test_admin_reset_password_empty_new_password(self):
        """Test réinitialisation avec nouveau mot de passe vide"""
        with self.assertRaises(CustomError):
            self.auth_service.admin_reset_password(self.test_user.id, "")

    def test_admin_reset_password_none_new_password(self):
        """Test réinitialisation avec nouveau mot de passe None"""
        with self.assertRaises(CustomError):
            self.auth_service.admin_reset_password(self.test_user.id, None)

    def test_login_after_admin_reset_password(self):
        """Test login après réinitialisation par admin"""
        new_password = "AdminReset456!"
        
        # Réinitialiser le mot de passe
        self.auth_service.admin_reset_password(self.test_user.id, new_password)

        # Vérifier que l'ancien mot de passe ne fonctionne plus
        with self.assertRaises(CustomError):
            self.auth_service.login("john@example.com", "Password123!")

        # Vérifier que le nouveau mot de passe fonctionne
        token = self.auth_service.login("john@example.com", new_password)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_admin_reset_password_different_from_change_password(self):
        """Test que admin_reset_password ne nécessite pas l'ancien mot de passe"""
        new_password = "AdminReset456!"
        
        # admin_reset_password ne devrait pas lever d'erreur même avec un mauvais ancien mot de passe
        # car il ne vérifie pas l'ancien mot de passe
        updated_user = self.auth_service.admin_reset_password(
            self.test_user.id, new_password
        )
        
        # Vérifier que le mot de passe a été changé
        self.assertTrue(verify_password(updated_user.password, new_password))

    def test_admin_reset_password_valid_password_requirements(self):
        """Test que admin_reset_password accepte les mots de passe valides"""
        valid_passwords = [
            "ValidPass123!",
            "AnotherGood456@",
            "Complex789#Password",
            "Minimum8!",  # Exactement 8 caractères
            "VeryLongPasswordWithAllRequirements123!@#",
        ]
        
        for valid_password in valid_passwords:
            # Réinitialiser avec un mot de passe valide
            updated_user = self.auth_service.admin_reset_password(
                self.test_user.id, valid_password
            )
            
            # Vérifier que le mot de passe fonctionne
            self.assertTrue(verify_password(updated_user.password, valid_password))
            
            # Vérifier que le login fonctionne
            token = self.auth_service.login("john@example.com", valid_password)
            self.assertIsInstance(token, str)

    def test_admin_reset_password_persistence(self):
        """Test que la réinitialisation persiste en base de données"""
        new_password = "AdminReset456!"
        
        # Réinitialiser le mot de passe
        updated_user = self.auth_service.admin_reset_password(
            self.test_user.id, new_password
        )
        
        # Récupérer l'utilisateur depuis la base pour vérifier la persistance
        fresh_user = self.user_service.get_user_by_id(self.test_user.id)
        self.assertEqual(fresh_user.password, updated_user.password)
        
        # Vérifier que le login fonctionne avec les données persistées
        token = self.auth_service.login("john@example.com", new_password)
        self.assertIsInstance(token, str)

    def test_admin_reset_password_multiple_resets(self):
        """Test réinitialisations multiples par admin"""
        passwords = ["AdminReset1!", "AdminReset2!", "AdminReset3!"]
        
        for new_password in passwords:
            # Réinitialiser le mot de passe
            updated_user = self.auth_service.admin_reset_password(
                self.test_user.id, new_password
            )
            
            # Vérifier que le nouveau mot de passe fonctionne
            token = self.auth_service.login("john@example.com", new_password)
            self.assertIsInstance(token, str)
            
            # Vérifier que les anciens mots de passe ne fonctionnent plus
            old_passwords = ["Password123!"] + passwords[:passwords.index(new_password)]
            for old_password in old_passwords:
                if old_password != new_password:
                    with self.assertRaises(CustomError):
                        self.auth_service.login("john@example.com", old_password)


if __name__ == '__main__':
    unittest.main()