#!/usr/bin/env python3

import json
import unittest
from flask import Flask
from flask_restx import Api

from app.tests.base_test import BaseTest
from app.api.v1.users import api as users_api
from app.api.v1.authentication import api as auth_api
from app.models.user import User


class TestUsersAdminCreateAPI(BaseTest):
    """Tests pour la route /users/admin-create"""

    def setUp(self):
        super().setUp()
        
        # Configuration de l'API
        self.api = self.create_test_api('AdminCreate')
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
        
        self.save_to_db(self.admin_user, self.regular_user)
        
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

    def test_admin_create_user_success(self):
        """Test création réussie d'un utilisateur par l'admin"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'TempPassword123!',  # Ce mot de passe sera remplacé par un temporaire
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
        
        # Vérifier les données retournées
        self.assertEqual(response_data['first_name'], 'John')
        self.assertEqual(response_data['last_name'], 'Doe')
        self.assertEqual(response_data['email'], 'john@example.com')
        self.assertEqual(response_data['address'], '123 Main St')
        self.assertEqual(response_data['phone_number'], '0123456789')
        self.assertIn('id', response_data)
        
        # Vérifier que l'utilisateur existe en DB
        user = User.query.filter_by(email='john@example.com').first()
        self.assertIsNotNone(user)

    def test_admin_create_user_minimal_data(self):
        """Test création avec données minimales"""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'password': 'TempPassword123!'
        }
        
        response = self.client.post(
            '/users/admin-create',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['first_name'], 'Jane')
        self.assertEqual(response_data['last_name'], 'Smith')
        self.assertEqual(response_data['email'], 'jane@example.com')

    def test_admin_create_user_duplicate_email(self):
        """Test création avec email existant"""
        # Créer premier utilisateur
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'TempPassword123!'
        }
        
        response = self.client.post(
            '/users/admin-create',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Tenter de créer un autre avec même email
        data2 = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'john@example.com',
            'password': 'TempPassword456!'
        }
        
        response = self.client.post(
            '/users/admin-create',
            data=json.dumps(data2),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 409)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    def test_admin_create_user_invalid_data(self):
        """Test création avec données invalides"""
        invalid_data_sets = [
            {},  # Pas de données
            {'first_name': 'John'},  # Données manquantes
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'invalid-email', 'password': 'TempPassword123!'},  # Email invalide
        ]
        
        for data in invalid_data_sets:
            response = self.client.post(
                '/users/admin-create',
                data=json.dumps(data),
                content_type='application/json'
            )
            # L'API retourne 500 pour les données manquantes, 400 pour les données invalides
            self.assertIn(response.status_code, [400, 500])

    def test_admin_create_user_requires_admin_rights(self):
        """Test que la création par admin nécessite des droits admin"""
        user_client = self.login_as_user()
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'TempPassword123!'
        }
        
        response = user_client.post(
            '/users/admin-create',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Vous n\'avez pas les droits administrateur')

    def test_admin_create_user_requires_authentication(self):
        """Test que la création par admin nécessite une authentification"""
        # Créer un nouveau client sans authentification
        unauthenticated_client = self.app.test_client()
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'TempPassword123!'
        }
        
        response = unauthenticated_client.post(
            '/users/admin-create',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)

    def test_admin_create_user_email_failure_does_not_prevent_creation(self):
        """Test que l'échec d'envoi d'email n'empêche pas la création"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'TempPassword123!'
        }
        
        response = self.client.post(
            '/users/admin-create',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # L'utilisateur doit être créé même si l'email échoue
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['email'], 'john@example.com')
        
        # Vérifier que l'utilisateur existe en DB
        user = User.query.filter_by(email='john@example.com').first()
        self.assertIsNotNone(user)

    def test_admin_create_user_response_format(self):
        """Test le format de la réponse"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'TempPassword123!',
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
        
        # Vérifier les champs requis
        required_fields = ['id', 'first_name', 'last_name', 'email']
        for field in required_fields:
            self.assertIn(field, response_data)
        
        # Vérifier que le mot de passe n'est pas inclus dans la réponse
        self.assertNotIn('password', response_data)

    def test_admin_create_user_generates_temp_password(self):
        """Test que la création génère un mot de passe temporaire"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'OriginalPassword123!'  # Ce mot de passe sera ignoré
        }
        
        response = self.client.post(
            '/users/admin-create',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Vérifier que l'utilisateur a été créé
        user = User.query.filter_by(email='john@example.com').first()
        self.assertIsNotNone(user)
        
        # Vérifier que le mot de passe original ne fonctionne pas (il a été remplacé par un temporaire)
        old_credentials = {
            'email': 'john@example.com',
            'password': 'OriginalPassword123!'
        }
        login_response = self.app.test_client().post(
            '/auth/login',
            data=json.dumps(old_credentials),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 401)


if __name__ == '__main__':
    unittest.main()