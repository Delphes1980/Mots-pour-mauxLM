#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api
from app.models.user import User

class TestUsersSearchPartialAPI(BaseTest):
    """Tests API users search partial - Tests pour /users/search-partial"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.client = self.app.test_client()

        # Créer utilisateurs
        self.admin_user = User(
            email='admin@test.com',
            password='Password123!',
            first_name='Admin',
            last_name='Test',
            is_admin=True
        )
        self.user1 = User(
            email='john.doe@example.com',
            password='Password123!',
            first_name='John',
            last_name='Doe',
            is_admin=False
        )
        self.user2 = User(
            email='jane.doe@example.com',
            password='Password123!',
            first_name='Jane',
            last_name='Doe',
            is_admin=False
        )
        self.save_to_db(self.admin_user, self.user1, self.user2)
        self.login_as_admin()

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_search_partial_success(self):
        """Test recherche partielle réussie"""
        response = self.client.get('/users/search-partial?email=doe')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        emails = [u['email'] for u in response_data]
        self.assertIn('john.doe@example.com', emails)
        self.assertIn('jane.doe@example.com', emails)

    def test_search_partial_no_results(self):
        """Test recherche partielle sans résultats"""
        response = self.client.get('/users/search-partial?email=nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_search_partial_missing_parameter(self):
        """Test recherche partielle sans paramètre"""
        response = self.client.get('/users/search-partial')
        self.assertEqual(response.status_code, 400)

    def test_search_partial_requires_admin(self):
        """Test que la recherche partielle nécessite des droits admin"""
        # Créer client utilisateur normal
        user_client = self.app.test_client()
        credentials = {'email': 'john.doe@example.com', 'password': 'Password123!'}
        user_client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        
        response = user_client.get('/users/search-partial?email=doe')
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()