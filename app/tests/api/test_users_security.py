#!/usr/bin/env python3

import json
import unittest
from flask_jwt_extended import create_access_token

from app.tests.base_test import BaseTest
from app.api.v1.users import api as users_api
from app.api.v1.authentication import api as auth_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.appointment import Appointment


class TestUsersSecurity(BaseTest):
    """Tests de sécurité pour l'API users"""

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
        self.api = self.create_test_api('Security')
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

    def test_all_admin_endpoints_require_authentication(self):
        """Test que tous les endpoints admin nécessitent une authentification"""
        # Client sans authentification
        no_auth_client = self.app.test_client()

        endpoints = [
            ('GET', '/users/'),
            ('GET', '/users/search?email=test@example.com'),
            ('GET', f'/users/{self.regular_user.id}'),
            ('PATCH', f'/users/{self.regular_user.id}', {'first_name': 'Test'}),
            ('DELETE', f'/users/{self.regular_user.id}'),
            ('POST', f'/users/{self.regular_user.id}/reset-password'),
        ]

        for method, url, *data in endpoints:
            payload = data[0] if data else None

            if method == 'GET':
                response = no_auth_client.get(url)
            elif method == 'PATCH':
                response = no_auth_client.patch(
                    url,
                    data=json.dumps(payload) if payload else '{}',
                    content_type='application/json'
                )
            elif method == 'DELETE':
                response = no_auth_client.delete(url)
            elif method == 'POST':
                response = no_auth_client.post(url)

            self.assertEqual(response.status_code, 401, 
                           f"Endpoint {method} {url} devrait retourner 401 sans token")

    def test_all_admin_endpoints_require_admin_rights(self):
        """Test que tous les endpoints admin nécessitent des droits admin"""
        # Se connecter en tant qu'utilisateur normal
        user_client = self.login_as_user()

        endpoints = [
            ('GET', '/users/'),
            ('GET', '/users/search?email=test@example.com'),
            ('GET', f'/users/{self.regular_user.id}'),
            ('DELETE', f'/users/{self.regular_user.id}'),
            ('POST', f'/users/{self.regular_user.id}/reset-password'),
        ]

        for method, url in endpoints:
            if method == 'GET':
                response = user_client.get(url)
            elif method == 'DELETE':
                response = user_client.delete(url)
            elif method == 'POST':
                response = user_client.post(url)

            self.assertEqual(response.status_code, 403, 
                           f"Endpoint {method} {url} devrait retourner 403 pour utilisateur non-admin")

    def test_user_can_only_update_own_account(self):
        """Test qu'un utilisateur ne peut modifier que son propre compte"""
        # Créer un autre utilisateur
        other_user = User(
            email='other@test.com',
            password='Password123!',
            first_name='Other',
            last_name='User',
            is_admin=False
        )
        self.save_to_db(other_user)

        # Se connecter en tant qu'utilisateur normal
        user_client = self.login_as_user()

        # Tenter de modifier le compte d'un autre utilisateur
        update_data = {'first_name': 'Hacked'}
        response = user_client.patch(
            f'/users/{other_user.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    def test_user_can_update_own_account(self):
        """Test qu'un utilisateur peut modifier son propre compte"""
        # Se connecter en tant qu'utilisateur normal
        user_client = self.login_as_user()

        # Modifier son propre compte
        update_data = {'first_name': 'Updated'}
        response = user_client.patch(
            f'/users/{self.regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['first_name'], 'Updated')

    def test_user_can_change_own_password(self):
        """Test qu'un utilisateur peut changer son propre mot de passe"""
        # Se connecter en tant qu'utilisateur normal
        user_client = self.login_as_user()

        # Changer son mot de passe
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

    def test_user_cannot_change_other_password(self):
        """Test qu'un utilisateur ne peut pas changer le mot de passe d'un autre"""
        # Créer un autre utilisateur
        other_user = User(
            email='other@test.com',
            password='Password123!',
            first_name='Other',
            last_name='User',
            is_admin=False
        )
        self.save_to_db(other_user)

        # Se connecter en tant qu'utilisateur normal
        user_client = self.login_as_user()

        # Tenter de changer le mot de passe d'un autre
        update_data = {
            'old_password': 'Password123!',
            'new_password': 'NewPassword456!'
        }
        response = user_client.patch(
            f'/users/{other_user.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_change_password_directly(self):
        """Test qu'un admin ne peut pas changer directement le mot de passe"""
        # Se connecter en tant qu'admin
        self.login_as_admin()

        # Tenter de changer le mot de passe directement
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

    def test_admin_must_use_reset_password_endpoint(self):
        """Test qu'un admin doit utiliser l'endpoint reset-password"""
        # Se connecter en tant qu'admin
        self.login_as_admin()

        # Utiliser l'endpoint reset-password
        response = self.client.post(f'/users/{self.regular_user.id}/reset-password')

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Mot de passe réinitialisé avec succès')

    def test_invalid_jwt_token(self):
        """Test avec token JWT invalide"""
        # Client avec cookie invalide
        invalid_client = self.app.test_client()
        invalid_client.set_cookie('access_token_cookie', 'invalid_token')

        response = invalid_client.get('/users/')

        self.assertEqual(response.status_code, 422)  # JWT invalide

    def test_admin_can_access_all_endpoints(self):
        """Test que l'admin peut accéder à tous les endpoints"""
        # Se connecter en tant qu'admin
        self.login_as_admin()

        # Créer le ghost user nécessaire à la suppression
        ghost_data = {
            'first_name': 'Ghost',
            'last_name': 'User',
            'email': 'deleted@system.local',
            'password': 'Ghost#2025!'
        }
        self.client.post('/users/', data=json.dumps(ghost_data), content_type='application/json')

        # Créer un utilisateur test
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        create_response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(create_response.data)['id']

        # Test GET all
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)

        # Test GET by ID
        response = self.client.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)

        # Test search
        response = self.client.get('/users/search?email=test@example.com')
        self.assertEqual(response.status_code, 200)

        # Test PATCH
        response = self.client.patch(
            f'/users/{user_id}',
            data=json.dumps({'first_name': 'Updated'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Test reset-password
        response = self.client.post(f'/users/{user_id}/reset-password')
        self.assertEqual(response.status_code, 200)

        # Test DELETE
        response = self.client.delete(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)

    def test_jwt_claims_validation(self):
        """Test validation des claims JWT"""
        # Créer un token sans claim is_admin
        with self.app.app_context():
            token_no_admin_claim = create_access_token(
                identity=str(self.admin_user.id)
            )

        # Client avec token sans claim is_admin
        no_claim_client = self.app.test_client()
        no_claim_client.set_cookie('access_token_cookie', token_no_admin_claim)

        response = no_claim_client.get('/users/')

        # Devrait être refusé car pas de claim is_admin
        self.assertEqual(response.status_code, 403)

    def test_expired_token_handling(self):
        """Test gestion token expiré"""
        # Simuler un token expiré avec un token invalide
        expired_client = self.app.test_client()
        expired_client.set_cookie('access_token_cookie', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.expired.token')

        response = expired_client.get('/users/')

        self.assertEqual(response.status_code, 422)

    def test_password_validation_in_creation(self):
        """Test validation du mot de passe lors de la création"""
        # Se connecter en tant qu'admin (pour pouvoir créer des utilisateurs)
        self.login_as_admin()

        # Test mots de passe invalides
        invalid_passwords = [
            'weak',  # Trop court, pas de majuscule, pas de caractère spécial
            'WeakPassword',  # Pas de chiffre, pas de caractère spécial
            'weakpassword123',  # Pas de majuscule, pas de caractère spécial
            'WeakPassword123',  # Pas de caractère spécial
            'weak123!',  # Pas de majuscule
        ]

        for password in invalid_passwords:
            data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': f'test{password}@example.com',
                'password': password
            }

            response = self.client.post(
                '/users/',
                data=json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400,
                           f"Mot de passe '{password}' devrait être rejeté")

    def test_password_validation_in_update(self):
        """Test validation du mot de passe lors de la mise à jour"""
        # Se connecter en tant qu'utilisateur normal
        user_client = self.login_as_user()

        # Test changement avec nouveau mot de passe invalide
        invalid_passwords = [
            'weak',
            'WeakPassword',
            'weakpassword123',
            'WeakPassword123',
            'weak123!',
        ]

        for password in invalid_passwords:
            update_data = {
                'old_password': 'Password123!',
                'new_password': password
            }

            response = user_client.patch(
                f'/users/{self.regular_user.id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400,
                           f"Nouveau mot de passe '{password}' devrait être rejeté")

    def test_email_validation_in_creation(self):
        """Test validation de l'email lors de la création"""
        # Se connecter en tant qu'admin
        self.login_as_admin()

        # Test emails invalides
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'test@',
            'test.example.com',
            '',
        ]

        for email in invalid_emails:
            data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': email,
                'password': 'Password123!'
            }

            response = self.client.post(
                '/users/',
                data=json.dumps(data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400, 
                           f"Email '{email}' devrait être rejeté")

    def test_email_validation_in_update(self):
        """Test validation de l'email lors de la mise à jour"""
        # Se connecter en tant qu'admin
        self.login_as_admin()

        # Créer un utilisateur
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        create_response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(create_response.data)['id']

        # Test mise à jour avec email invalide
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'test@',
            'test.example.com',
        ]

        for email in invalid_emails:
            update_data = {'email': email}

            response = self.client.patch(
                f'/users/{user_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400,
                           f"Email '{email}' devrait être rejeté")

    def test_get_me_requires_authentication(self):
        """Test que /users/me nécessite un token JWT"""
        response = self.client.get('/users/me')
        self.assertEqual(response.status_code, 401)

    def test_get_me_rejects_invalid_token(self):
        """Test que /users/me rejette un token invalide"""
        response = self.client.get(
            '/users/me',
            headers={'Authorization': 'Bearer faketoken123'}
        )
        self.assertEqual(response.status_code, 401)  # JWT invalide ou manquant → 401 attendu avec token en cookie


if __name__ == '__main__':
    unittest.main()
