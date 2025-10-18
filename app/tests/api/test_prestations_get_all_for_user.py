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


class TestGetAllPrestationsForUser(BaseTest):
    """Tests complets pour la route GET /prestations/ (utilisateur connecté)"""

    def setUp(self):
        super().setUp()

        # Configuration de l'API
        self.api = self.create_test_api('GetAllPrestations')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(prestations_api, path='/prestations')

        self.client = self.app.test_client()

        # Création des utilisateurs
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

    def login_as_user(self):
        credentials = {
            'email': 'user@test.com',
            'password': 'UserPass123!'
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    # 🔹 Test API
    def test_get_all_prestations_api(self):
        """API : récupération des prestations visibles"""
        self.save_to_db(
            Prestation(name='Hypnose thérapeutique'),
            Prestation(name='Ghost prestation')
        )
        self.login_as_user()
        response = self.client.get('/prestations/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        names = [p['name'] for p in data]
        self.assertIn('Hypnose thérapeutique', names)
        self.assertNotIn('Ghost prestation', names)

    # 🔹 Test Sécurité
    def test_unauthenticated_user_cannot_access_prestations(self):
        """Sécurité : accès interdit sans authentification"""
        response = self.client.get('/prestations/')
        self.assertEqual(response.status_code, 401)

    # 🔹 Test Intégration
    def test_integration_visible_prestations_only(self):
        """Intégration : seules les prestations visibles sont retournées"""
        self.save_to_db(
            Prestation(name='Massage'),
            Prestation(name='Ghost prestation'),
            Prestation(name='Thérapie')
        )
        self.login_as_user()
        response = self.client.get('/prestations/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        names = [p['name'] for p in data]
        self.assertIn('Massage', names)
        self.assertIn('Thérapie', names)
        self.assertNotIn('Ghost prestation', names)

    # 🔹 Test Unitaire (service)
    def test_service_returns_only_visible_prestations(self):
        """Unitaire : le service filtre correctement les prestations"""
        from app.services.PrestationService import PrestationService
        self.save_to_db(
            Prestation(name='Ghost prestation'),
            Prestation(name='Hypnose')
        )
        service = PrestationService()
        prestations = service.get_all_prestations_for_user()
        names = [p.name for p in prestations]
        self.assertIn('Hypnose', names)
        self.assertNotIn('Ghost prestation', names)

    # 🔹 Test Unitaire (repository)
    def test_repository_excludes_ghost_prestation(self):
        """Unitaire : le repository exclut la prestation fantôme"""
        from app.persistence.PrestationRepository import PrestationRepository
        self.save_to_db(
            Prestation(name='Ghost prestation'),
            Prestation(name='Massage')
        )
        repo = PrestationRepository()
        repo.db = self.db
        repo.model_class = Prestation
        prestations = repo.get_all_prestations_for_user()
        names = [p.name for p in prestations]
        self.assertIn('Massage', names)
        self.assertNotIn('Ghost prestation', names)


if __name__ == '__main__':
    unittest.main()
