#!/usr/bin/env python3

import json
import unittest
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import create_access_token

from app.tests.base_test import BaseTest
from app.api.v1.users import api as users_api
from app.api.v1.authentication import api as auth_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.appointment import Appointment


class TestUsersIntegration(BaseTest):
    """Tests d'intégration pour l'API users avec vraie DB"""
    
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
        self.api = self.create_test_api('Integration')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        
        # Client de test
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
        
        # Se connecter pour obtenir les cookies JWT
        self.login_as_admin()

    def login_as_admin(self):
        """Se connecter en tant qu'admin et garder les cookies"""
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
        # Créer un nouveau client pour l'utilisateur normal
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
    
    def test_create_user_integration(self):
        """Test création complète d'un utilisateur"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'Password123!',
            'address': '123 Main St',
            'phone_number': '0123456789'
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
        
        # Vérifier en DB
        user = User.query.filter_by(email='john@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.address, '123 Main St')
        
        # Vérifier que le mot de passe est hashé
        self.assertNotEqual(user.password, 'Password123!')
        self.assertTrue(user.password.startswith('$2b$'))
    
    def test_get_all_users_integration(self):
        """Test récupération de tous les utilisateurs"""
        # Créer des utilisateurs en DB
        users_data = [
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com', 'password': 'Password123!'},
            {'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com', 'password': 'Password456!'},
        ]
        
        for data in users_data:
            self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        
        response = self.client.get('/users/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 4)  # 2 de setUp + 2 créés
        
        emails = [u['email'] for u in response_data]
        self.assertIn('john@example.com', emails)
        self.assertIn('jane@example.com', emails)
        self.assertIn('admin@test.com', emails)
        self.assertIn('user@test.com', emails)
    
    def test_search_user_integration(self):
        """Test recherche utilisateur par email"""
        # Créer utilisateur en DB
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'Password123!'
        }
        self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        
        response = self.client.get('/users/search?email=john@example.com')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['email'], 'john@example.com')
        self.assertEqual(response_data['first_name'], 'John')
    
    def test_get_user_by_id_integration(self):
        """Test récupération utilisateur par ID"""
        # Créer utilisateur
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'Password123!'
        }
        create_response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        response = self.client.get(f'/users/{user_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['id'], user_id)
        self.assertEqual(response_data['email'], 'john@example.com')
    
    def test_update_user_integration(self):
        """Test mise à jour utilisateur"""
        # Créer utilisateur
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'Password123!'
        }
        create_response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        # Mettre à jour
        update_data = {
            'first_name': 'Johnny',
            'address': '456 Oak St',
            'phone_number': '0987654321'
        }
        response = self.client.patch(
            f'/users/{user_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['first_name'], 'Johnny')
        self.assertEqual(response_data['address'], '456 Oak St')
        self.assertEqual(response_data['phone_number'], '0987654321')
        
        # Vérifier en DB
        self.db.session.expire_all()
        updated_user = User.query.get(user_id)
        self.assertEqual(updated_user.first_name, 'Johnny')
        self.assertEqual(updated_user.address, '456 Oak St')
    
    def test_delete_user_integration(self):
        """Test suppression utilisateur"""
        # Créer utilisateur
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'Password123!'
        }
        create_response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        response = self.client.delete(f'/users/{user_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Utilisateur supprimé avec succès')
        
        # Vérifier suppression en DB
        self.db.session.expire_all()
        deleted_user = User.query.get(user_id)
        self.assertIsNone(deleted_user)
    
    def test_workflow_complet_user(self):
        """Test workflow complet : créer -> lire -> modifier -> supprimer"""
        # 1. Créer
        data = {
            'first_name': 'Workflow',
            'last_name': 'Test',
            'email': 'workflow@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(
            '/users/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        user_id = json.loads(response.data)['id']
        
        # 2. Lire
        response = self.client.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['first_name'], 'Workflow')
        
        # 3. Modifier
        update_data = {'first_name': 'Workflow Modified'}
        response = self.client.patch(
            f'/users/{user_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['first_name'], 'Workflow Modified')
        
        # 4. Supprimer
        response = self.client.delete(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
    
    def test_password_change_workflow(self):
        """Test workflow complet de changement de mot de passe"""
        # Créer utilisateur
        data = {
            'first_name': 'Password',
            'last_name': 'Test',
            'email': 'password@example.com',
            'password': 'Password123!'
        }
        create_response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        # Se connecter en tant que cet utilisateur
        new_client = self.app.test_client()
        login_data = {
            'email': 'password@example.com',
            'password': 'Password123!'
        }
        response = new_client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Changer le mot de passe
        update_data = {
            'old_password': 'Password123!',
            'new_password': 'NewPassword456!'
        }
        response = new_client.patch(
            f'/users/{user_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que l'ancien mot de passe ne fonctionne plus
        old_login = {
            'email': 'password@example.com',
            'password': 'Password123!'
        }
        response = self.app.test_client().post(
            '/auth/login',
            data=json.dumps(old_login),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        
        # Vérifier que le nouveau mot de passe fonctionne
        new_login = {
            'email': 'password@example.com',
            'password': 'NewPassword456!'
        }
        response = self.app.test_client().post(
            '/auth/login',
            data=json.dumps(new_login),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_admin_reset_password_workflow(self):
        """Test workflow complet de réinitialisation par admin"""
        # Créer utilisateur
        data = {
            'first_name': 'Reset',
            'last_name': 'Test',
            'email': 'reset@example.com',
            'password': 'Password123!'
        }
        create_response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        # Vérifier que l'utilisateur peut se connecter avec son mot de passe
        login_data = {
            'email': 'reset@example.com',
            'password': 'Password123!'
        }
        response = self.app.test_client().post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Admin réinitialise le mot de passe
        response = self.client.post(f'/users/{user_id}/reset-password')
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que l'ancien mot de passe ne fonctionne plus
        response = self.app.test_client().post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
    
    def test_security_no_admin_rights(self):
        """Test sécurité : utilisateur non-admin ne peut pas accéder aux fonctions admin"""
        # Se connecter en tant qu'utilisateur normal
        user_client = self.login_as_user()
        
        # Créer un utilisateur test
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        create_response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        endpoints = [
            ('GET', '/users/', None),
            ('GET', f'/users/search?email=test@example.com', None),
            ('GET', f'/users/{user_id}', None),
            ('DELETE', f'/users/{user_id}', None),
            ('POST', f'/users/{user_id}/reset-password', None),
        ]
        
        for method, url, data in endpoints:
            if method == 'GET':
                response = user_client.get(url)
            elif method == 'DELETE':
                response = user_client.delete(url)
            elif method == 'POST':
                response = user_client.post(url)
            
            self.assertEqual(response.status_code, 403)
    
    def test_security_no_token(self):
        """Test sécurité : pas de token JWT"""
        # Client sans authentification
        no_auth_client = self.app.test_client()
        
        endpoints = [
            ('GET', '/users/'),
            ('GET', '/users/search?email=test@example.com'),
            ('GET', f'/users/{self.regular_user.id}'),
            ('PATCH', f'/users/{self.regular_user.id}'),
            ('DELETE', f'/users/{self.regular_user.id}'),
            ('POST', f'/users/{self.regular_user.id}/reset-password'),
        ]
        
        for method, url in endpoints:
            if method == 'GET':
                response = no_auth_client.get(url)
            elif method == 'PATCH':
                response = no_auth_client.patch(url, data='{}', content_type='application/json')
            elif method == 'DELETE':
                response = no_auth_client.delete(url)
            elif method == 'POST':
                response = no_auth_client.post(url)
            
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()