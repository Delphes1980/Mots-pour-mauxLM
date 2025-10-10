#!/usr/bin/env python3

import json
import unittest
from flask import Flask
from flask_restx import Api

from app.tests.base_test import BaseTest
from app.api.v1.prestations import api as prestations_api
from app.api.v1.authentication import api as auth_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.appointment import Appointment


class TestPrestationsUnitSimple(BaseTest):
    """Tests unitaires pour l'API prestations sans mocks - utilise la vraie DB"""
    
    def setUp(self):
        super().setUp()
        
        # Configuration de l'API via BaseTest
        self.api = self.create_test_api('PrestationsUnitSimple')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(prestations_api, path='/prestations')
        
        # Client de test
        self.client = self.app.test_client()
        
        # Créer utilisateur admin avec mot de passe conforme
        self.admin_user = User(
            email='admin@test.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='Test',
            is_admin=True
        )
        self.save_to_db(self.admin_user)
        
        # Se connecter pour obtenir les cookies JWT
        self.login_as_admin()
    
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
            'password': 'AdminPass123!'
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_create_prestation_success(self):
        """Test création réussie d'une prestation"""
        data = {'name': 'Massage Relaxant'}
        response = self.client.post(
            '/prestations/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Massage Relaxant')
    
    def test_create_prestation_invalid_data(self):
        """Test création avec données invalides"""
        data = {}  # Nom manquant
        response = self.client.post(
            '/prestations/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_get_all_prestations_success(self):
        """Test récupération de toutes les prestations"""
        # Créer une prestation
        prestation = Prestation(name='Test Prestation')
        self.save_to_db(prestation)
        
        response = self.client.get('/prestations/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 1)
    
    def test_search_prestation_found(self):
        """Test recherche prestation existante"""
        # Créer une prestation
        prestation = Prestation(name='Massage Thérapeutique')
        self.save_to_db(prestation)
        
        response = self.client.get('/prestations/search?name=Massage Thérapeutique')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Massage Thérapeutique')
    
    def test_search_prestation_not_found(self):
        """Test recherche prestation inexistante"""
        response = self.client.get('/prestations/search?name=Inexistant')
        
        self.assertEqual(response.status_code, 404)
    
    def test_search_prestation_missing_name(self):
        """Test recherche sans paramètre name"""
        response = self.client.get('/prestations/search')
        
        self.assertEqual(response.status_code, 400)
    
    def test_get_prestation_by_id_found(self):
        """Test récupération par ID existant"""
        # Créer une prestation
        prestation = Prestation(name='Test Prestation')
        self.save_to_db(prestation)
        
        response = self.client.get(f'/prestations/{prestation.id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Test Prestation')
    
    def test_update_prestation_success(self):
        """Test mise à jour réussie"""
        # Créer une prestation
        prestation = Prestation(name='Ancien Nom')
        self.save_to_db(prestation)
        
        data = {'name': 'Nouveau Nom'}
        response = self.client.put(
            f'/prestations/{prestation.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['name'], 'Nouveau Nom')
    
    def test_delete_prestation_success(self):
        """Test suppression réussie"""
        # Créer une prestation
        prestation = Prestation(name='À Supprimer')
        self.save_to_db(prestation)
        
        response = self.client.delete(f'/prestations/{prestation.id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Prestation supprimée avec succès')


if __name__ == '__main__':
    unittest.main()