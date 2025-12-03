#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api
from app.models.user import User


class TestUsersForgotPassword(BaseTest):
    """Tests pour la fonctionnalité mot de passe oublié - API"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.client = self.app.test_client()

        # Créer utilisateur de test
        self.test_user = User(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='Password123!',
            is_admin=False
        )
        self.save_to_db(self.test_user)

    def test_forgot_password_success(self):
        """Test demande de réinitialisation réussie"""
        data = {'email': 'test@example.com'}
        
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Email de réinitialisation envoyé avec succès')
        
        # Vérifier que l'ancien mot de passe ne fonctionne plus
        old_credentials = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        login_response = self.client.post(
            '/auth/login',
            data=json.dumps(old_credentials),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 401)

    def test_forgot_password_user_not_found(self):
        """Test avec email inexistant"""
        data = {'email': 'nonexistent@example.com'}
        
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    def test_forgot_password_missing_email(self):
        """Test sans email"""
        data = {}
        
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('requis', response_data['error'])

    def test_forgot_password_empty_email(self):
        """Test avec email vide"""
        data = {'email': ''}
        
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    def test_forgot_password_invalid_email_format(self):
        """Test avec format d'email invalide"""
        invalid_emails = [
            'invalid-email',
            'test@',
            '@example.com',
            'test..test@example.com',
            'test@example',
            'test@.com'
        ]
        
        for email in invalid_emails:
            data = {'email': email}
            
            response = self.client.post(
                '/users/forgot-password',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            self.assertIn(response.status_code, [400, 404])
            response_data = json.loads(response.data)
            self.assertIn('error', response_data)

    def test_forgot_password_no_authentication_required(self):
        """Test que la route ne nécessite pas d'authentification"""
        # Pas de login préalable
        data = {'email': 'test@example.com'}
        
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Doit réussir même sans authentification
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_multiple_requests(self):
        """Test plusieurs demandes successives"""
        data = {'email': 'test@example.com'}
        
        # Première demande
        response1 = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        # Deuxième demande immédiate
        response2 = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)

    def test_forgot_password_case_insensitive_email(self):
        """Test avec différentes casses d'email"""
        # Créer utilisateur avec email en minuscules
        user = User(
            first_name='Case',
            last_name='Test',
            email='case@example.com',
            password='Password123!',
            is_admin=False
        )
        self.save_to_db(user)
        
        # Test avec différentes casses
        email_variations = [
            'case@example.com',
            'Case@example.com',
            'CASE@EXAMPLE.COM',
            'CaSe@ExAmPlE.cOm'
        ]
        
        for email in email_variations:
            data = {'email': email}
            
            response = self.client.post(
                '/users/forgot-password',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            # Selon l'implémentation, peut être 200 ou 404
            self.assertIn(response.status_code, [200, 404])

    def test_forgot_password_admin_user(self):
        """Test avec utilisateur admin"""
        admin_user = User(
            first_name='Admin',
            last_name='Test',
            email='admin@example.com',
            password='Password123!',
            is_admin=True
        )
        self.save_to_db(admin_user)
        
        data = {'email': 'admin@example.com'}
        
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Email de réinitialisation envoyé avec succès')

    def test_forgot_password_json_content_type_required(self):
        """Test que le Content-Type JSON est requis"""
        data = 'email=test@example.com'
        
        response = self.client.post(
            '/users/forgot-password',
            data=data,
            content_type='application/x-www-form-urlencoded'
        )
        
        # Doit échouer sans JSON
        self.assertIn(response.status_code, [400, 415])


if __name__ == '__main__':
    unittest.main()