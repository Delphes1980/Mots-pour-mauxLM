#!/usr/bin/env python3

import json
import unittest
from flask import Flask
from flask_restx import Api

from app.tests.base_test import BaseTest
from app.api.v1.users import api as users_api
from app.api.v1.authentication import api as auth_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.appointment import Appointment


class TestUsersUnitSimple(BaseTest):
    """Tests unitaires pour l'API users sans mocks - utilise la vraie DB"""
    
    def test_base_is_clean(self):
        self.tearDown()
        users = User.query.all()
        prestations = Prestation.query.all()
        reviews = Review.query.all()
        appointments = Appointment.query.all()
        self.assertEqual(len(users), 0)
        self.assertEqual(len(prestations), 0)
        self.assertEqual(len(reviews), 0)
        self.assertEqual(len(appointments), 0)
        self.setUp()

    def setUp(self):
        super().setUp()
        
        # Configuration de l'API via BaseTest
        self.api = self.create_test_api('UnitSimple')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        
        # Client de test
        self.client = self.app.test_client()
        
        # Créer utilisateurs avec mots de passe conformes
        self.admin_user = User(
            email='admin@test.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='Test',
            is_admin=True
        )
        self.regular_user = User(
            email='user@test.com',
            password='UserPass123!',
            first_name='User',
            last_name='Test',
            is_admin=False
        )
        self.save_to_db(self.admin_user, self.regular_user)
        
        # Se connecter pour obtenir les cookies JWT
        self.login_as_admin()

    def login_as_admin(self):
        """Se connecter en tant qu'admin et garder les cookies"""
        credentials = {
            'email': 'admin@test.com',
            'password': 'AdminPass123!'
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_create_user_success(self):
        """Test création réussie d'un utilisateur"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(
            '/users/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['first_name'], 'John')
        self.assertEqual(response_data['email'], 'john@example.com')
    
    def test_create_user_invalid_data(self):
        """Test création avec données invalides"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid-email',
            'password': 'weak'
        }
        response = self.client.post(
            '/users/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_get_all_users_success(self):
        """Test récupération de tous les utilisateurs"""
        response = self.client.get('/users/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 2)  # admin + regular user
    
    def test_admin_rights_required(self):
        """Test que les droits admin sont requis"""
        # Se connecter en tant qu'utilisateur normal
        user_client = self.app.test_client()
        credentials = {
            'email': 'user@test.com',
            'password': 'UserPass123!'
        }
        user_client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        
        response = user_client.get('/users/')
        
        self.assertEqual(response.status_code, 403)
    
    def test_admin_reset_password_success(self):
        """Test réinitialisation de mot de passe par admin"""
        response = self.client.post(f'/users/{self.regular_user.id}/reset-password')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Mot de passe réinitialisé avec succès')

    def test_get_me_returns_current_user(self):
        """Test que /users/me retourne les infos de l'utilisateur connecté via cookie JWT"""
        credentials = {
            'email': 'user@test.com',
            'password': 'UserPass123!'
        }

        # Connexion → le cookie JWT est stocké dans self.client
        login_response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 200)

        # Appel direct à /users/me avec le même client
        response = self.client.get('/users/me')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['email'], 'user@test.com')
        self.assertEqual(data['first_name'], 'User')
        self.assertEqual(data['last_name'], 'Test')

    def test_search_user_by_email_success(self):
        """Test que /users/search retourne un utilisateur existant (admin requis)"""
        # Se connecter en tant qu'admin
        credentials = {
            'email': 'admin@test.com',
            'password': 'AdminPass123!'
        }
        self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )

        # Créer un utilisateur à rechercher
        user = User(
            email='john.doe@example.com',
            password='Secure123!',
            first_name='John',
            last_name='Doe'
        )
        self.save_to_db(user)

        response = self.client.get('/users/search?email=john.doe@example.com')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['email'], 'john.doe@example.com')
        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['last_name'], 'Doe')

    def test_search_user_by_email_not_found(self):
        """Test que /users/search retourne 404 si l'utilisateur n'existe pas"""
        # Se connecter en tant qu'admin
        credentials = {
            'email': 'admin@test.com',
            'password': 'AdminPass123!'
        }
        self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )

        response = self.client.get('/users/search?email=unknown@example.com')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()