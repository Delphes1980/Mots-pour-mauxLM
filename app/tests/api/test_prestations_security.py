#!/usr/bin/env python3

import json
import unittest
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import create_access_token

from app.tests.base_test import BaseTest
from app.api.v1.prestations import api as prestations_api
from app.api.v1.authentication import api as auth_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.appointment import Appointment


class TestPrestationsSecurity(BaseTest):
    """Tests de sécurité pour l'API prestations"""
    
    def setUp(self):
        super().setUp()
        
        # Configuration de l'API via BaseTest
        self.api = self.create_test_api('Security')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(prestations_api, path='/prestations')
        
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
    
    def test_base_is_clean(self):
        users = User.query.all()
        prestations = Prestation.query.all()
        reviews = Review.query.all()
        appointments = Appointment.query.all()
        self.assertEqual(len(users), 0)
        self.assertEqual(len(prestations), 0)
        self.assertEqual(len(reviews), 0)
        self.assertEqual(len(appointments), 0)

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
    
    def test_all_endpoints_require_authentication(self):
        """Test que tous les endpoints nécessitent une authentification"""
        prestation = Prestation(name='Test Prestation')
        self.save_to_db(prestation)
        
        # Client sans authentification
        no_auth_client = self.app.test_client()
        
        endpoints = [
            ('POST', '/prestations/', {'name': 'Test'}),
            ('GET', '/prestations/', None),
            ('GET', '/prestations/search?name=Test', None),
            ('GET', f'/prestations/{prestation.id}', None),
            ('PUT', f'/prestations/{prestation.id}', {'name': 'Updated'}),
            ('DELETE', f'/prestations/{prestation.id}', None),
        ]
        
        for method, url, data in endpoints:
            if method == 'POST':
                response = no_auth_client.post(
                    url,
                    data=json.dumps(data) if data else None,
                    content_type='application/json'
                )
            elif method == 'PUT':
                response = no_auth_client.put(
                    url,
                    data=json.dumps(data) if data else None,
                    content_type='application/json'
                )
            elif method == 'DELETE':
                response = no_auth_client.delete(url)
            else:  # GET
                response = no_auth_client.get(url)
            
            self.assertEqual(response.status_code, 401, 
                           f"Endpoint {method} {url} devrait retourner 401 sans token")
    
    def test_all_endpoints_require_admin_rights(self):
        """Test que tous les endpoints nécessitent des droits admin"""
        prestation = Prestation(name='Test Prestation')
        self.save_to_db(prestation)
        
        # Se connecter en tant qu'utilisateur normal
        user_client = self.login_as_user()
        
        endpoints = [
            ('POST', '/prestations/', {'name': 'Test'}),
            ('GET', '/prestations/', None),
            ('GET', '/prestations/search?name=Test', None),
            ('GET', f'/prestations/{prestation.id}', None),
            ('PUT', f'/prestations/{prestation.id}', {'name': 'Updated'}),
            ('DELETE', f'/prestations/{prestation.id}', None),
        ]
        
        for method, url, data in endpoints:
            if method == 'POST':
                response = user_client.post(
                    url,
                    data=json.dumps(data) if data else None,
                    content_type='application/json'
                )
            elif method == 'PUT':
                response = user_client.put(
                    url,
                    data=json.dumps(data) if data else None,
                    content_type='application/json'
                )
            elif method == 'DELETE':
                response = user_client.delete(url)
            else:  # GET
                response = user_client.get(url)
            
            self.assertEqual(response.status_code, 403, 
                           f"Endpoint {method} {url} devrait retourner 403 pour utilisateur non-admin")
    
    def test_invalid_jwt_token(self):
        """Test avec token JWT invalide"""
        # Client avec cookie invalide
        invalid_client = self.app.test_client()
        invalid_client.set_cookie('access_token_cookie', 'invalid_token')
        
        response = invalid_client.get('/prestations/')
        
        self.assertEqual(response.status_code, 422)  # JWT invalide
    
    def test_admin_can_access_all_endpoints(self):
        """Test que l'admin peut accéder à tous les endpoints"""
        # Se connecter en tant qu'admin
        self.login_as_admin()
        
        prestation = Prestation(name='Test Admin Access')
        self.save_to_db(prestation)
        
        # Test GET all
        response = self.client.get('/prestations/')
        self.assertEqual(response.status_code, 200)
        
        # Test GET by ID
        response = self.client.get(f'/prestations/{prestation.id}')
        self.assertEqual(response.status_code, 200)
        
        # Test search
        response = self.client.get('/prestations/search?name=Test Admin Access')
        self.assertEqual(response.status_code, 200)
        
        # Test PUT
        response = self.client.put(
            f'/prestations/{prestation.id}',
            data=json.dumps({'name': 'Updated Admin Access'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Test POST
        response = self.client.post(
            '/prestations/',
            data=json.dumps({'name': 'New Admin Prestation'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Test DELETE
        response = self.client.delete(f'/prestations/{prestation.id}')
        self.assertEqual(response.status_code, 200)
    
    def test_jwt_claims_validation(self):
        """Test validation des claims JWT"""
        # Créer un utilisateur admin mais se connecter avec un token sans claim is_admin
        with self.app.app_context():
            token_no_admin_claim = create_access_token(
                identity=str(self.admin_user.id)
            )
        
        # Client avec token sans claim is_admin
        no_claim_client = self.app.test_client()
        no_claim_client.set_cookie('access_token_cookie', token_no_admin_claim)
        
        response = no_claim_client.get('/prestations/')
        
        # Devrait être refusé car pas de claim is_admin
        self.assertEqual(response.status_code, 403)
    
    def test_expired_token_handling(self):
        """Test gestion token expiré"""
        # Simuler un token expiré avec un token invalide
        expired_client = self.app.test_client()
        expired_client.set_cookie('access_token_cookie', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.expired.token')
        
        response = expired_client.get('/prestations/')
        
        self.assertEqual(response.status_code, 422)


if __name__ == '__main__':
    unittest.main()