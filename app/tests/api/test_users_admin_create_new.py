#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api
from app.models.user import User

class TestUsersAdminCreateAPI(BaseTest):
    """Tests API users admin create - Tests pour /users/admin-create"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.client = self.app.test_client()

        # Créer admin
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
        self.login_as_admin()

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def login_as_user(self):
        credentials = {'email': 'user@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_admin_create_user_success(self):
        """Test création d'utilisateur par admin réussie"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': '123 Main St',
            'phone_number': '0123456789'
        }
        response = self.client.post(
            '/users/admin-create',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['first_name'], 'John')
        self.assertEqual(response_data['email'], 'john@example.com')

    def test_admin_create_user_duplicate_email(self):
        """Test création avec email existant"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'admin@test.com'  # Email déjà existant
        }
        response = self.client.post(
            '/users/admin-create',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)

    def test_admin_create_user_requires_admin(self):
        """Test que la création par admin nécessite des droits admin"""
        self.login_as_user()
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com'
        }
        response = self.client.post(
            '/users/admin-create',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_create_user_invalid_data(self):
        """Test création avec données invalides"""
        invalid_data_sets = [
            {},  # Pas de données
            {'first_name': 'John'},  # Données manquantes
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'invalid-email'},  # Email invalide
        ]
        
        for data in invalid_data_sets:
            response = self.client.post(
                '/users/admin-create',
                data=json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()