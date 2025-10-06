#!/usr/bin/env python3

import json
import unittest
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import create_access_token

from app.tests.base_test import BaseTest
from app.api.v1.prestations import api as prestations_api
from app.models.user import User
from app.models.prestation import Prestation


class TestPrestationsSecurity(BaseTest):
    """Tests de sécurité pour l'API prestations"""
    
    def setUp(self):
        super().setUp()
        
        # Configuration de l'API via BaseTest
        self.api = self.create_test_api('Security')
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
        
        # Tokens JWT
        with self.app.app_context():
            self.admin_token = create_access_token(
                identity=str(self.admin_user.id),
                additional_claims={'is_admin': True}
            )
            self.user_token = create_access_token(
                identity=str(self.regular_user.id),
                additional_claims={'is_admin': False}
            )
            self.invalid_token = 'invalid.jwt.token'
    
    def get_auth_headers(self, token):
        return {'Authorization': f'Bearer {token}'}
    
    def test_all_endpoints_require_authentication(self):
        """Test que tous les endpoints nécessitent une authentification"""
        prestation = Prestation(name='Test Prestation')
        self.save_to_db(prestation)
        
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
                response = self.client.post(
                    url,
                    data=json.dumps(data) if data else None,
                    content_type='application/json'
                )
            elif method == 'PUT':
                response = self.client.put(
                    url,
                    data=json.dumps(data) if data else None,
                    content_type='application/json'
                )
            elif method == 'DELETE':
                response = self.client.delete(url)
            else:  # GET
                response = self.client.get(url)
            
            self.assertEqual(response.status_code, 401, 
                           f"Endpoint {method} {url} devrait retourner 401 sans token")
    
    def test_all_endpoints_require_admin_rights(self):
        """Test que tous les endpoints nécessitent des droits admin"""
        prestation = Prestation(name='Test Prestation')
        self.save_to_db(prestation)
        
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
                response = self.client.post(
                    url,
                    data=json.dumps(data) if data else None,
                    content_type='application/json',
                    headers=self.get_auth_headers(self.user_token)
                )
            elif method == 'PUT':
                response = self.client.put(
                    url,
                    data=json.dumps(data) if data else None,
                    content_type='application/json',
                    headers=self.get_auth_headers(self.user_token)
                )
            elif method == 'DELETE':
                response = self.client.delete(
                    url,
                    headers=self.get_auth_headers(self.user_token)
                )
            else:  # GET
                response = self.client.get(
                    url,
                    headers=self.get_auth_headers(self.user_token)
                )
            
            self.assertEqual(response.status_code, 403, 
                           f"Endpoint {method} {url} devrait retourner 403 pour utilisateur non-admin")
    
    def test_invalid_jwt_token(self):
        """Test avec token JWT invalide"""
        response = self.client.get(
            '/prestations/',
            headers=self.get_auth_headers(self.invalid_token)
        )
        
        self.assertEqual(response.status_code, 422)  # JWT invalide
    
    def test_malformed_authorization_header(self):
        """Test avec header Authorization malformé"""
        malformed_headers = [
            {'Authorization': 'InvalidFormat'},
            {'Authorization': 'Bearer'},
            {'Authorization': f'Basic {self.admin_token}'},
        ]
        
        for headers in malformed_headers:
            response = self.client.get('/prestations/', headers=headers)
            self.assertIn(response.status_code, [401, 422])
    
    def test_admin_can_access_all_endpoints(self):
        """Test que l'admin peut accéder à tous les endpoints"""
        prestation = Prestation(name='Test Admin Access')
        self.save_to_db(prestation)
        
        # Test GET all
        response = self.client.get(
            '/prestations/',
            headers=self.get_auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        
        # Test GET by ID
        response = self.client.get(
            f'/prestations/{prestation.id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        
        # Test search
        response = self.client.get(
            '/prestations/search?name=Test Admin Access',
            headers=self.get_auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        
        # Test PUT
        response = self.client.put(
            f'/prestations/{prestation.id}',
            data=json.dumps({'name': 'Updated Admin Access'}),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        
        # Test POST
        response = self.client.post(
            '/prestations/',
            data=json.dumps({'name': 'New Admin Prestation'}),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 201)
        
        # Test DELETE
        response = self.client.delete(
            f'/prestations/{prestation.id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
    
    def test_jwt_claims_validation(self):
        """Test validation des claims JWT"""
        # Token sans claim is_admin
        token_no_admin_claim = create_access_token(
            identity=str(self.admin_user.id)
        )
        
        response = self.client.get(
            '/prestations/',
            headers=self.get_auth_headers(token_no_admin_claim)
        )
        
        # Devrait être refusé car pas de claim is_admin
        self.assertEqual(response.status_code, 403)
    
    def test_expired_token_handling(self):
        """Test gestion token expiré"""
        # Créer un token avec durée très courte (nécessite configuration spéciale)
        # Pour ce test, on simule juste avec un token invalide
        expired_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.expired.token'
        
        response = self.client.get(
            '/prestations/',
            headers=self.get_auth_headers(expired_token)
        )
        
        self.assertEqual(response.status_code, 422)


if __name__ == '__main__':
    unittest.main()