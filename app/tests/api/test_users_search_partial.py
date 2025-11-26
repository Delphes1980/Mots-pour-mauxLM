#!/usr/bin/env python3

import json
import unittest
from flask import Flask
from flask_restx import Api

from app.tests.base_test import BaseTest
from app.api.v1.users import api as users_api
from app.api.v1.authentication import api as auth_api
from app.models.user import User


class TestUsersSearchPartialAPI(BaseTest):
    """Tests pour la route /users/search-partial"""

    def setUp(self):
        super().setUp()
        
        # Configuration de l'API
        self.api = self.create_test_api('SearchPartial')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        
        # Client de test
        self.client = self.app.test_client()
        
        # Créer utilisateurs de test
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
        
        # Créer des utilisateurs avec différents emails pour les tests de recherche
        self.user1 = User(
            email='john.doe@example.com',
            password='Password123!',
            first_name='John',
            last_name='Doe',
            is_admin=False
        )
        self.user2 = User(
            email='jane.smith@example.com',
            password='Password123!',
            first_name='Jane',
            last_name='Smith',
            is_admin=False
        )
        self.user3 = User(
            email='bob.johnson@company.com',
            password='Password123!',
            first_name='Bob',
            last_name='Johnson',
            is_admin=False
        )
        
        self.save_to_db(self.admin_user, self.regular_user, self.user1, self.user2, self.user3)
        
        # Se connecter en tant qu'admin
        self.login_as_admin()

    def login_as_admin(self):
        """Se connecter en tant qu'admin"""
        credentials = {
            'email': 'admin@test.com',
            'password': 'Password123!'
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def login_as_user(self):
        """Se connecter en tant qu'utilisateur normal"""
        self.user_client = self.app.test_client()
        credentials = {
            'email': 'user@test.com',
            'password': 'Password123!'
        }
        response = self.user_client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        return self.user_client

    def test_search_partial_success_single_match(self):
        """Test recherche partielle avec un seul résultat"""
        response = self.client.get('/users/search-partial?email=john.doe')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['email'], 'john.doe@example.com')
        self.assertEqual(response_data[0]['first_name'], 'John')

    def test_search_partial_success_multiple_matches(self):
        """Test recherche partielle avec plusieurs résultats"""
        response = self.client.get('/users/search-partial?email=example')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        
        emails = [user['email'] for user in response_data]
        self.assertIn('john.doe@example.com', emails)
        self.assertIn('jane.smith@example.com', emails)

    def test_search_partial_success_domain_search(self):
        """Test recherche partielle par domaine"""
        response = self.client.get('/users/search-partial?email=company')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['email'], 'bob.johnson@company.com')

    def test_search_partial_no_matches(self):
        """Test recherche partielle sans résultats"""
        response = self.client.get('/users/search-partial?email=nonexistent')
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    def test_search_partial_case_insensitive(self):
        """Test recherche partielle insensible à la casse"""
        response = self.client.get('/users/search-partial?email=JOHN.DOE')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['email'], 'john.doe@example.com')

    def test_search_partial_missing_email_parameter(self):
        """Test recherche partielle sans paramètre email"""
        response = self.client.get('/users/search-partial')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Le fragment d\'email est requis')

    def test_search_partial_empty_email_parameter(self):
        """Test recherche partielle avec paramètre email vide"""
        response = self.client.get('/users/search-partial?email=')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    def test_search_partial_requires_admin_rights(self):
        """Test que la recherche partielle nécessite des droits admin"""
        user_client = self.login_as_user()
        
        response = user_client.get('/users/search-partial?email=john.doe')
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Vous n\'avez pas les droits administrateur')

    def test_search_partial_requires_authentication(self):
        """Test que la recherche partielle nécessite une authentification"""
        # Créer un nouveau client sans authentification
        unauthenticated_client = self.app.test_client()
        
        response = unauthenticated_client.get('/users/search-partial?email=john.doe')
        
        self.assertEqual(response.status_code, 401)

    def test_search_partial_response_format(self):
        """Test le format de la réponse de la recherche partielle"""
        response = self.client.get('/users/search-partial?email=john.doe')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Vérifier que c'est une liste
        self.assertIsInstance(response_data, list)
        
        if len(response_data) > 0:
            user = response_data[0]
            # Vérifier les champs requis
            required_fields = ['id', 'first_name', 'last_name', 'email', 'is_admin', 'created_at']
            for field in required_fields:
                self.assertIn(field, user)
            
            # Vérifier que le mot de passe n'est pas inclus
            self.assertNotIn('password', user)

    def test_search_partial_special_characters(self):
        """Test recherche partielle avec caractères spéciaux"""
        # Créer un utilisateur avec des caractères spéciaux
        special_user = User(
            email='test+special@domain.co.uk',
            password='Password123!',
            first_name='Special',
            last_name='User',
            is_admin=False
        )
        self.save_to_db(special_user)
        
        response = self.client.get('/users/search-partial?email=special')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['email'], 'test+special@domain.co.uk')


if __name__ == '__main__':
    unittest.main()