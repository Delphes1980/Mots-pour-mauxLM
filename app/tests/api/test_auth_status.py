#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.models.user import User

class TestAuthStatusAPI(BaseTest):
    """Tests API auth status - Tests pour /auth/status"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.client = self.app.test_client()

        # Créer utilisateurs
        self.admin_user = User(
            email='admin@test.com',
            password='Password123!',
            first_name='Admin',
            last_name='Test',
            is_admin=True
        )
        self.regular_user = User(
            email='user@test.com',
            password='Password123!',
            first_name='User',
            last_name='Test',
            is_admin=False
        )
        self.save_to_db(self.admin_user, self.regular_user)

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def login_as_user(self):
        credentials = {'email': 'user@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_auth_status_admin_success(self):
        """Test statut de connexion admin"""
        self.login_as_admin()
        response = self.client.get('/auth/status')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Connecté')
        self.assertEqual(response_data['user_id'], str(self.admin_user.id))
        self.assertTrue(response_data['is_admin'])

    def test_auth_status_user_success(self):
        """Test statut de connexion utilisateur normal"""
        self.login_as_user()
        response = self.client.get('/auth/status')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Connecté')
        self.assertEqual(response_data['user_id'], str(self.regular_user.id))
        self.assertFalse(response_data['is_admin'])

    def test_auth_status_without_login(self):
        """Test statut sans être connecté"""
        response = self.client.get('/auth/status')
        self.assertEqual(response.status_code, 401)

    def test_auth_status_after_logout(self):
        """Test statut après déconnexion"""
        self.login_as_user()
        self.client.post('/auth/logout')
        response = self.client.get('/auth/status')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()