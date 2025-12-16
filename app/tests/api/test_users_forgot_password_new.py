#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api
from app.models.user import User

class TestUsersForgotPasswordAPI(BaseTest):
    """Tests API users forgot password - Tests pour /users/forgot-password"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.client = self.app.test_client()

        # Créer utilisateur
        self.user = User(
            email='user@test.com',
            password='Password123!',
            first_name='User',
            last_name='Test',
            is_admin=False
        )
        self.save_to_db(self.user)

    def test_forgot_password_success(self):
        """Test demande de réinitialisation réussie"""
        data = {'email': 'user@test.com'}
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Email de réinitialisation envoyé avec succès')

    def test_forgot_password_user_not_found(self):
        """Test avec utilisateur inexistant"""
        data = {'email': 'nonexistent@test.com'}
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_forgot_password_missing_email(self):
        """Test sans email"""
        data = {}
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_forgot_password_invalid_email(self):
        """Test avec email invalide"""
        data = {'email': 'invalid-email'}
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()