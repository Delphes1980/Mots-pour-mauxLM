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


class TestPrestationsAPI(BaseTest):
    """Tests API prestations - Tests de bout en bout avec vraie DB"""
    
    def setUp(self):
        super().setUp()
        
        # Configuration de l'API via BaseTest
        self.api = self.create_test_api('Main')
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
    
    def test_create_prestation_success(self):
        """Test création réussie d'une prestation"""
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
        self.assertIn('id', response_data)
        
        # Vérifier en DB
        prestation = Prestation.query.filter_by(name='Massage Thérapeutique').first()
        self.assertIsNotNone(prestation)
    
    def test_create_prestation_duplicate_name(self):
        """Test création prestation avec nom existant"""
        # Créer première prestation
        prestation = Prestation(name='Massage Unique')
        self.save_to_db(prestation)
        
        # Tenter de créer une prestation avec le même nom
        data = {'name': 'Massage Unique'}
        response = self.client.post(
            '/prestations/',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        # Devrait échouer (selon la logique métier)
        self.assertIn(response.status_code, [400, 409])
    
    def test_create_prestation_invalid_data(self):
        """Test création avec données invalides"""
        invalid_data_sets = [
            {},  # Pas de nom
            {'name': ''},  # Nom vide
            {'name': None},  # Nom null
            {'invalid_field': 'value'},  # Champ invalide
        ]
        
        for data in invalid_data_sets:
            response = self.client.post(
                '/prestations/',
                data=json.dumps(data),
                content_type='application/json',
                headers=self.get_auth_headers(self.admin_token)
            )
            self.assertEqual(response.status_code, 400)
    
    def test_get_all_prestations_empty(self):
        """Test récupération quand aucune prestation"""
        response = self.client.get(
            '/prestations/',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 0)
    
    def test_get_all_prestations_with_data(self):
        """Test récupération avec prestations existantes"""
        prestations = [
            Prestation(name='Massage'),
            Prestation(name='Thérapie'),
            Prestation(name='Acupuncture')
        ]
        self.save_to_db(*prestations)
        
        response = self.client.get(
            '/prestations/',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 3)
        
        names = [p['name'] for p in response_data]
        self.assertIn('Massage', names)
        self.assertIn('Thérapie', names)
        self.assertIn('Acupuncture', names)
    
    def test_search_prestation_found(self):
        """Test recherche prestation existante"""
        prestation = Prestation(name='Réflexologie Plantaire')
        self.save_to_db(prestation)
        
        response = self.client.get(
            '/prestations/search?name=Réflexologie Plantaire',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Réflexologie Plantaire')
    
    def test_search_prestation_not_found(self):
        """Test recherche prestation inexistante"""
        response = self.client.get(
            '/prestations/search?name=Prestation Inexistante',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_prestation_by_id_found(self):
        """Test récupération par ID existant"""
        prestation = Prestation(name='Ostéopathie')
        self.save_to_db(prestation)
        
        response = self.client.get(
            f'/prestations/{prestation.id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Ostéopathie')
        self.assertEqual(response_data['id'], str(prestation.id))
    
    def test_get_prestation_by_id_not_found(self):
        """Test récupération par ID inexistant"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        
        response = self.client.get(
            f'/prestations/{fake_id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_update_prestation_success(self):
        """Test mise à jour réussie"""
        prestation = Prestation(name='Massage Simple')
        self.save_to_db(prestation)
        
        data = {'name': 'Massage Thérapeutique Avancé'}
        response = self.client.put(
            f'/prestations/{prestation.id}',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Massage Thérapeutique Avancé')
        
        # Vérifier en DB
        self.db.session.expire_all()
        updated_prestation = Prestation.query.get(prestation.id)
        self.assertEqual(updated_prestation.name, 'Massage Thérapeutique Avancé')
    
    def test_update_prestation_not_found(self):
        """Test mise à jour prestation inexistante"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        
        data = {'name': 'Nouveau Nom'}
        response = self.client.put(
            f'/prestations/{fake_id}',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_prestation_success(self):
        """Test suppression réussie"""
        prestation = Prestation(name='Prestation à Supprimer')
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
    
    def test_delete_prestation_not_found(self):
        """Test suppression prestation inexistante"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        
        response = self.client.delete(
            f'/prestations/{fake_id}',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()