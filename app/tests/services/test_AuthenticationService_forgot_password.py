#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.services.AuthenticationService import AuthenticationService
from app.utils import CustomError


class TestAuthenticationServiceForgotPassword(BaseTest):
    """Tests pour la réinitialisation de mot de passe par email - Service"""

    def setUp(self):
        super().setUp()
        self.service = AuthenticationService()
        
        # Créer utilisateur de test
        self.test_user = User(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='Password123!',
            is_admin=False
        )
        self.save_to_db(self.test_user)

    def test_reset_password_by_email_success(self):
        """Test réinitialisation réussie par email"""
        new_password = 'NewTemp123!'
        
        result = self.service.reset_password_by_email('test@example.com', new_password)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.email, 'test@example.com')
        
        # Vérifier que le mot de passe a été changé
        from app.utils import verify_password
        updated_user = User.query.get(self.test_user.id)
        self.assertTrue(verify_password(updated_user.password, new_password))

    def test_reset_password_by_email_user_not_found(self):
        """Test avec email inexistant"""
        with self.assertRaises(CustomError) as context:
            self.service.reset_password_by_email('nonexistent@example.com', 'NewTemp123!')
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn('User not found', str(context.exception))

    def test_reset_password_by_email_invalid_email(self):
        """Test avec email invalide"""
        invalid_emails = [
            '',
            'invalid-email',
            'test@',
            '@example.com',
            None
        ]
        
        for email in invalid_emails:
            with self.assertRaises(CustomError) as context:
                self.service.reset_password_by_email(email, 'NewTemp123!')
            
            self.assertEqual(context.exception.status_code, 400)

    def test_reset_password_by_email_invalid_password(self):
        """Test avec mot de passe invalide"""
        invalid_passwords = [
            '',
            'weak',
            '12345678',
            'password',
            'PASSWORD',
            'Password',
            'Pass123',  # Trop court
            None
        ]
        
        for password in invalid_passwords:
            with self.assertRaises(CustomError) as context:
                self.service.reset_password_by_email('test@example.com', password)
            
            self.assertEqual(context.exception.status_code, 400)

    def test_reset_password_by_email_valid_password_formats(self):
        """Test avec différents formats de mots de passe valides"""
        valid_passwords = [
            'NewTemp123!',
            'ValidPass1@',
            'Strong#Pass2',
            'MySecure$3',
            'Test&Pass4'
        ]
        
        for password in valid_passwords:
            result = self.service.reset_password_by_email('test@example.com', password)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.email, 'test@example.com')
            
            # Vérifier que le mot de passe a été changé
            from app.utils import verify_password
            updated_user = User.query.get(self.test_user.id)
            self.assertTrue(verify_password(updated_user.password, password))

    def test_reset_password_by_email_case_sensitivity(self):
        """Test sensibilité à la casse de l'email"""
        # Test avec différentes casses
        email_variations = [
            'test@example.com',
            'Test@example.com',
            'TEST@EXAMPLE.COM',
            'TeSt@ExAmPlE.cOm'
        ]
        
        for email in email_variations:
            try:
                result = self.service.reset_password_by_email(email, 'NewTemp123!')
                # Si ça réussit, vérifier que c'est le bon utilisateur
                self.assertEqual(result.email, 'test@example.com')
            except CustomError as e:
                # Si ça échoue, doit être 404 (user not found)
                self.assertEqual(e.status_code, 404)

    def test_reset_password_by_email_admin_user(self):
        """Test réinitialisation pour utilisateur admin"""
        admin_user = User(
            first_name='Admin',
            last_name='Test',
            email='admin@example.com',
            password='AdminPass123!',
            is_admin=True
        )
        self.save_to_db(admin_user)
        
        result = self.service.reset_password_by_email('admin@example.com', 'NewAdminPass123!')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.email, 'admin@example.com')
        self.assertTrue(result.is_admin)

    def test_reset_password_by_email_multiple_users(self):
        """Test avec plusieurs utilisateurs"""
        # Créer utilisateurs supplémentaires
        users = []
        names = ['Alice', 'Bob', 'Charlie']
        for i in range(3):
            user = User(
                first_name=names[i],
                last_name='Test',
                email=f'user{i}@example.com',
                password='Password123!',
                is_admin=False
            )
            users.append(user)
            self.save_to_db(user)
        
        # Réinitialiser le mot de passe pour chaque utilisateur
        for i, user in enumerate(users):
            new_password = f'NewPass{i}123!'
            result = self.service.reset_password_by_email(user.email, new_password)
            
            self.assertEqual(result.email, user.email)
            
            # Vérifier que seul ce mot de passe a été changé
            from app.utils import verify_password
            updated_user = User.query.get(user.id)
            self.assertTrue(verify_password(updated_user.password, new_password))

    def test_reset_password_by_email_preserves_other_fields(self):
        """Test que la réinitialisation préserve les autres champs"""
        original_first_name = self.test_user.first_name
        original_last_name = self.test_user.last_name
        original_is_admin = self.test_user.is_admin
        original_created_at = self.test_user.created_at
        
        result = self.service.reset_password_by_email('test@example.com', 'NewTemp123!')
        
        # Vérifier que les autres champs sont préservés
        self.assertEqual(result.first_name, original_first_name)
        self.assertEqual(result.last_name, original_last_name)
        self.assertEqual(result.is_admin, original_is_admin)
        self.assertEqual(result.created_at, original_created_at)

    def test_reset_password_by_email_database_consistency(self):
        """Test cohérence de la base de données"""
        new_password = 'NewTemp123!'
        
        # Compter les utilisateurs avant
        users_count_before = User.query.count()
        
        result = self.service.reset_password_by_email('test@example.com', new_password)
        
        # Compter les utilisateurs après
        users_count_after = User.query.count()
        
        # Le nombre d'utilisateurs ne doit pas changer
        self.assertEqual(users_count_before, users_count_after)
        
        # Vérifier que l'utilisateur existe toujours avec le même ID
        updated_user = User.query.get(self.test_user.id)
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.email, 'test@example.com')


if __name__ == '__main__':
    unittest.main()