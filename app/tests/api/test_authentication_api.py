#!/usr/bin/env python3

import json
import unittest
from flask_jwt_extended import create_access_token

from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.appointment import Appointment
from app.utils import verify_password


class TestAuthenticationAPI(BaseTest):
    """Tests API authentication - Tests de bout en bout avec vraie DB"""
    
    def setUp(self):
        super().setUp()
        
        # Configuration de l'API via BaseTest
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        
        # Client de test
        self.client = self.app.test_client()
        
        # Créer utilisateur de test
        self.test_user = User(
            email='test@example.com',
            password='Password123!',
            first_name='Test',
            last_name='User',
            is_admin=False
        )
        self.admin_user = User(
            email='admin@example.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        self.save_to_db(self.test_user, self.admin_user)
    
    def test_base_is_clean(self):
        # Faire un nettoyage complet avant de tester
        self.db.session.rollback()
        for model in [Appointment, Review, Prestation, User]:
            self.db.session.query(model).delete()
        self.db.session.commit()
        
        # Maintenant tester que la base est vraiment vide
        users = User.query.all()
        prestations = Prestation.query.all()
        reviews = Review.query.all()
        appointments = Appointment.query.all()
        self.assertEqual(len(users), 0)
        self.assertEqual(len(prestations), 0)
        self.assertEqual(len(reviews), 0)
        self.assertEqual(len(appointments), 0)


    def test_login_success_regular_user(self):
        """Test connexion réussie utilisateur normal"""
        credentials = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Authentification réussie')
        
        # Vérifier que les cookies JWT sont définis
        cookies = response.headers.getlist('Set-Cookie')
        access_token_set = any('access_token_cookie=' in cookie for cookie in cookies)
        self.assertTrue(access_token_set)
    
    def test_login_success_admin_user(self):
        """Test connexion réussie utilisateur admin"""
        credentials = {
            'email': 'admin@example.com',
            'password': 'AdminPass123!'
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Authentification réussie')
        
        # Vérifier que les cookies JWT sont définis
        cookies = response.headers.getlist('Set-Cookie')
        access_token_set = any('access_token_cookie=' in cookie for cookie in cookies)
        self.assertTrue(access_token_set)
    
    def test_login_invalid_email(self):
        """Test connexion avec email inexistant"""
        credentials = {
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        # Peut être 400 (email invalide) ou 401 (authentification échouée)
        self.assertIn(response.status_code, [400, 401])
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_login_invalid_password(self):
        """Test connexion avec mot de passe incorrect"""
        credentials = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], 'Authentification échouée')
    
    def test_login_missing_email(self):
        """Test connexion sans email"""
        credentials = {
            'password': 'Password123!'
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_login_missing_password(self):
        """Test connexion sans mot de passe"""
        credentials = {
            'email': 'test@example.com'
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_login_empty_credentials(self):
        """Test connexion avec données vides"""
        credentials = {}
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_login_invalid_email_format(self):
        """Test connexion avec format email invalide"""
        credentials = {
            'email': 'invalid-email-format',
            'password': 'Password123!'
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        # Devrait échouer soit à la validation soit à l'authentification
        self.assertIn(response.status_code, [400, 401])
    
    def test_login_empty_email(self):
        """Test connexion avec email vide"""
        credentials = {
            'email': '',
            'password': 'Password123!'
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        # Email vide devrait échouer à la validation ou à l'authentification
        self.assertIn(response.status_code, [400, 401])
    
    def test_login_empty_password(self):
        """Test connexion avec mot de passe vide"""
        credentials = {
            'email': 'test@example.com',
            'password': ''
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        # Mot de passe vide devrait échouer à l'authentification
        self.assertEqual(response.status_code, 401)
    
    def test_logout_success(self):
        """Test déconnexion réussie"""
        # D'abord se connecter via l'API pour obtenir les cookies
        credentials = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        login_response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        
        # Vérifier que la connexion a réussi
        self.assertEqual(login_response.status_code, 200)
        
        # Maintenant tester la déconnexion (les cookies sont automatiquement inclus)
        response = self.client.post('/auth/logout')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Déconnexion réussie')
        
        # Vérifier que des cookies de suppression sont présents
        cookies = response.headers.getlist('Set-Cookie')
        # Vérifier qu'au moins un cookie access_token_cookie est présent (pour suppression)
        access_token_cookie_present = any('access_token_cookie' in cookie for cookie in cookies)
        self.assertTrue(access_token_cookie_present, f"Aucun cookie access_token_cookie trouvé dans: {cookies}")
    
    def test_logout_without_token(self):
        """Test déconnexion sans être connecté"""
        response = self.client.post('/auth/logout')
        
        # Devrait échouer car pas de token JWT
        self.assertEqual(response.status_code, 401)
    
    def test_logout_invalid_token(self):
        """Test déconnexion avec token invalide"""
        # Simuler un cookie avec token invalide
        self.client.set_cookie('access_token_cookie', 'invalid_token')
        
        response = self.client.post('/auth/logout')
        
        # Devrait échouer car token invalide
        self.assertEqual(response.status_code, 422)  # JWT decode error
    
    def test_login_no_content_type(self):
        """Test connexion sans Content-Type"""
        credentials = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials)
            # Pas de content_type
        )
        
        # Devrait échouer ou traiter différemment
        self.assertIn(response.status_code, [400, 415])
    
    def test_login_malformed_json(self):
        """Test connexion avec JSON malformé"""
        malformed_json = '{"email": "test@example.com", "password": "Password123!"'  # JSON incomplet
        
        response = self.client.post(
            '/auth/login',
            data=malformed_json,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()