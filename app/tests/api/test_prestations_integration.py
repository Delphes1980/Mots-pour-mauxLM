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


class TestPrestationsIntegration(BaseTest):
    """Tests d'intégration pour l'API prestations avec vraie DB"""
    
    def setUp(self):
        super().setUp()
        
        # Configuration de l'API via BaseTest
        self.api = self.create_test_api('Integration')
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
    
    def get_auth_headers(self, token):
        return {'Authorization': f'Bearer {token}'}
    
    def test_create_prestation_integration(self):
        """Test création complète d'une prestation"""
        data = {'name': 'Massage Thérapeutique'}
        
        response = self.client.post(
            '/prestations/',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Massage Thérapeutique')
        
        # Vérifier en DB
        prestation = Prestation.query.filter_by(name='Massage Thérapeutique').first()
        self.assertIsNotNone(prestation)
        self.assertEqual(prestation.name, 'Massage Thérapeutique')
    
    def test_get_all_prestations_integration(self):
        """Test récupération de toutes les prestations"""
        # Créer des prestations en DB
        prestation1 = Prestation(name='Massage')
        prestation2 = Prestation(name='Thérapie')
        self.save_to_db(prestation1, prestation2)
        
        response = self.client.get(
            '/prestations/',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        
        names = [p['name'] for p in response_data]
        self.assertIn('Massage', names)
        self.assertIn('Thérapie', names)
    
    def test_search_prestation_integration(self):
        """Test recherche prestation par nom"""
        # Créer prestation en DB
        prestation = Prestation(name='Réflexologie')
        self.save_to_db(prestation)
        
        response = self.client.get(
            '/prestations/search?name=Réflexologie',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Réflexologie')
    
    def test_get_prestation_by_id_integration(self):
        """Test récupération prestation par ID"""
        prestation = Prestation(name='Acupuncture')
        self.save_to_db(prestation)
        
        response = self.client.get(
            f'/prestations/{prestation.id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Acupuncture')
    
    def test_update_prestation_integration(self):
        """Test mise à jour prestation"""
        prestation = Prestation(name='Massage Simple')
        self.save_to_db(prestation)
        
        data = {'name': 'Massage Relaxant'}
        response = self.client.put(
            f'/prestations/{prestation.id}',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Massage Relaxant')
        
        # Vérifier en DB
        self.db.session.expire_all()
        updated_prestation = Prestation.query.get(prestation.id)
        self.assertEqual(updated_prestation.name, 'Massage Relaxant')
    
    def test_delete_prestation_integration(self):
        """Test suppression prestation"""
        prestation = Prestation(name='Prestation à supprimer')
        self.save_to_db(prestation)
        prestation_id = prestation.id
        
        response = self.client.delete(
            f'/prestations/{prestation_id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Prestation supprimée avec succès')
        
        # Vérifier suppression en DB
        self.db.session.expire_all()
        deleted_prestation = Prestation.query.get(prestation_id)
        self.assertIsNone(deleted_prestation)
    
    def test_workflow_complet_prestation(self):
        """Test workflow complet : créer -> lire -> modifier -> supprimer"""
        # 1. Créer
        data = {'name': 'Workflow Test'}
        response = self.client.post(
            '/prestations/',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 201)
        prestation_id = json.loads(response.data)['id']
        
        # 2. Lire
        response = self.client.get(
            f'/prestations/{prestation_id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['name'], 'Workflow Test')
        
        # 3. Modifier
        data = {'name': 'Workflow Test Modifié'}
        response = self.client.put(
            f'/prestations/{prestation_id}',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['name'], 'Workflow Test Modifié')
        
        # 4. Supprimer
        response = self.client.delete(
            f'/prestations/{prestation_id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        self.assertEqual(response.status_code, 200)
    
    def test_security_no_admin_rights(self):
        """Test sécurité : utilisateur non-admin ne peut pas accéder"""
        endpoints = [
            ('POST', '/prestations/', {'name': 'Test'}),
            ('GET', '/prestations/', None),
            ('GET', '/prestations/search?name=Test', None),
        ]
        
        for method, url, data in endpoints:
            if method == 'POST':
                response = self.client.post(
                    url,
                    data=json.dumps(data),
                    content_type='application/json',
                    headers=self.get_auth_headers(self.user_token)
                )
            else:
                response = self.client.get(
                    url,
                    headers=self.get_auth_headers(self.user_token)
                )
            
            self.assertEqual(response.status_code, 403)
    
    def test_security_no_token(self):
        """Test sécurité : pas de token JWT"""
        response = self.client.get('/prestations/')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()