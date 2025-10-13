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


class TestUsersAPI(BaseTest):
    """Tests API users - Tests de bout en bout avec vraie DB"""

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
        self.api = self.create_test_api('Main')
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
        if response.status_code != 200:
            error_data = response.get_json()
            # Si c'est une erreur UTF-8, recréer l'API
            if error_data and 'utf-8' in str(error_data.get('error', '')):
                self.api = self.create_test_api('Retry')
                self.api.add_namespace(auth_api, path='/auth')
                self.api.add_namespace(users_api, path='/users')
                self.client = self.app.test_client()
                # Retry login
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
    
    def test_create_user_success(self):
        """Test création réussie d'un utilisateur"""
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
        self.assertEqual(response_data['last_name'], 'Doe')
        self.assertEqual(response_data['email'], 'john@example.com')
        self.assertEqual(response_data['address'], '123 Main St')
        self.assertEqual(response_data['phone_number'], '0123456789')
        self.assertIn('id', response_data)
        
        # Vérifier en DB
        user = User.query.filter_by(email='john@example.com').first()
        self.assertIsNotNone(user)
    
    def test_create_user_minimal_data(self):
        """Test création avec données minimales"""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(
            '/users/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['first_name'], 'Jane')
        self.assertEqual(response_data['last_name'], 'Smith')
        self.assertEqual(response_data['email'], 'jane@example.com')
    
    def test_create_user_duplicate_email(self):
        """Test création avec email existant"""
        # Créer premier utilisateur
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
        
        # Tenter de créer un autre avec même email
        data2 = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'john@example.com',
            'password': 'Password456!'
        }
        
        response = self.client.post(
            '/users/',
            data=json.dumps(data2),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 409)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_create_user_invalid_data(self):
        """Test création avec données invalides"""
        invalid_data_sets = [
            {},  # Pas de données
            {'first_name': 'John'},  # Données manquantes
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'invalid-email', 'password': 'Password123!'},  # Email invalide
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com', 'password': 'weak'},  # Mot de passe faible
        ]
        
        for data in invalid_data_sets:
            response = self.client.post(
                '/users/',
                data=json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
    
    def test_get_all_users_empty(self):
        """Test récupération quand aucun utilisateur (sauf admin/user de test)"""
        response = self.client.get('/users/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        # Il y a déjà admin_user et regular_user créés dans setUp
        self.assertEqual(len(response_data), 2)
    
    def test_get_all_users_with_data(self):
        """Test récupération avec utilisateurs existants"""
        # Créer des utilisateurs supplémentaires
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
    
    def test_get_all_users_requires_admin(self):
        """Test que get_all_users nécessite des droits admin"""
        user_client = self.login_as_user()
        
        response = user_client.get('/users/')
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_search_user_found(self):
        """Test recherche utilisateur existant"""
        # Créer utilisateur
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
    
    def test_search_user_not_found(self):
        """Test recherche utilisateur inexistant"""
        response = self.client.get('/users/search?email=nonexistent@example.com')
        
        self.assertEqual(response.status_code, 404)
    
    def test_search_user_missing_email_parameter(self):
        """Test recherche sans paramètre email"""
        response = self.client.get('/users/search')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_get_user_by_id_found(self):
        """Test récupération par ID existant"""
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
    
    def test_get_user_by_id_not_found(self):
        """Test récupération par ID inexistant"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        
        response = self.client.get(f'/users/{fake_id}')
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_user_success(self):
        """Test mise à jour réussie"""
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
            'address': '456 Oak St'
        }
        response = self.client.patch(
            f'/users/{user_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['first_name'], 'Johnny')
        self.assertEqual(response_data['last_name'], 'Doe')  # Inchangé
        self.assertEqual(response_data['address'], '456 Oak St')
    
    def test_update_user_password_change(self):
        """Test changement de mot de passe par utilisateur normal"""
        # Se connecter en tant qu'utilisateur normal
        user_client = self.login_as_user()
        
        # Mettre à jour le mot de passe
        update_data = {
            'old_password': 'Password123!',
            'new_password': 'NewPassword456!'
        }
        response = user_client.patch(
            f'/users/{self.regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que l'ancien mot de passe ne fonctionne plus
        old_credentials = {
            'email': 'user@test.com',
            'password': 'Password123!'
        }
        response = self.app.test_client().post(
            '/auth/login',
            data=json.dumps(old_credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        
        # Vérifier que le nouveau mot de passe fonctionne
        new_credentials = {
            'email': 'user@test.com',
            'password': 'NewPassword456!'
        }
        response = self.app.test_client().post(
            '/auth/login',
            data=json.dumps(new_credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_update_user_admin_cannot_change_password_directly(self):
        """Test qu'un admin ne peut pas changer directement le mot de passe"""
        update_data = {
            'old_password': 'Password123!',
            'new_password': 'NewPassword456!'
        }
        response = self.client.patch(
            f'/users/{self.regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_update_user_not_found(self):
        """Test mise à jour utilisateur inexistant"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        
        update_data = {'first_name': 'Johnny'}
        response = self.client.patch(
            f'/users/{fake_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_user_success(self):
        """Test suppression réussie"""
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
    
    def test_delete_user_not_found(self):
        """Test suppression utilisateur inexistant"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        
        response = self.client.delete(f'/users/{fake_id}')
        
        self.assertEqual(response.status_code, 404)
    
    def test_admin_reset_password_success(self):
        """Test réinitialisation de mot de passe par admin"""
        # Créer utilisateur
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'Password123!'
        }
        create_response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(create_response.data)['id']
        
        response = self.client.post(f'/users/{user_id}/reset-password')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Mot de passe réinitialisé avec succès')
        
        # Vérifier que l'ancien mot de passe ne fonctionne plus
        old_credentials = {
            'email': 'john@example.com',
            'password': 'Password123!'
        }
        response = self.app.test_client().post(
            '/auth/login',
            data=json.dumps(old_credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
    
    def test_admin_reset_password_not_found(self):
        """Test réinitialisation mot de passe utilisateur inexistant"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        
        response = self.client.post(f'/users/{fake_id}/reset-password')
        
        self.assertEqual(response.status_code, 404)
    
    def test_admin_reset_password_requires_admin(self):
        """Test que reset-password nécessite des droits admin"""
        user_client = self.login_as_user()
        
        response = user_client.post(f'/users/{self.regular_user.id}/reset-password')
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)


if __name__ == '__main__':
    unittest.main()