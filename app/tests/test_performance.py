#!/usr/bin/env python3

import json
import time
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api
from app.api.v1.appointments import api as appointments_api
from app.api.v1.reviews import api as reviews_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review

class TestPerformance(BaseTest):
    """Tests de performance basiques"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.api.add_namespace(appointments_api, path='/appointments')
        self.api.add_namespace(reviews_api, path='/reviews')
        self.client = self.app.test_client()

        # Créer admin
        self.admin_user = User(
            email='admin@test.com',
            password='Password123!',
            first_name='Admin',
            last_name='Test',
            is_admin=True
        )
        self.save_to_db(self.admin_user)
        self.login_as_admin()

    def _get_suffix(self, index):
        """Helper pour générer des suffixes alphabétiques (0->A, 1->B...)"""
        return chr(65 + (index % 26))

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_user_creation_performance(self):
        """Test performance création d'utilisateurs"""
        start_time = time.time()

        for i in range(10):
            suffix = self._get_suffix(i)
            data = {
                'first_name': f'User{suffix}',
                'last_name': 'Test',
                'email': f'user{i}@test.com',
                'password': 'Password123!'
            }
            response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 201)

        end_time = time.time()
        duration = end_time - start_time

        # 10 utilisateurs en moins de 5 secondes
        self.assertLess(duration, 5.0, f"Création de 10 utilisateurs trop lente: {duration:.2f}s")

    def test_login_performance(self):
        """Test performance de connexion"""
        # Créer utilisateur
        user_data = {
            'first_name': 'Speed',
            'last_name': 'Test',
            'email': 'speed@test.com',
            'password': 'Password123!'
        }
        self.client.post('/users/', data=json.dumps(user_data), content_type='application/json')

        login_data = {'email': 'speed@test.com', 'password': 'Password123!'}

        start_time = time.time()
        response = self.client.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        duration = end_time - start_time

        # Connexion en moins de 1 seconde
        self.assertLess(duration, 1.0, f"Connexion trop lente: {duration:.2f}s")

    def test_bulk_data_retrieval_performance(self):
        """Test performance récupération de données en masse"""
        # Créer plusieurs utilisateurs et prestations
        users = []
        prestations = []

        for i in range(20):
            suffix = self._get_suffix(i)
            user = User(
                email=f'bulk{i}@test.com',
                password='Password123!',
                first_name=f'Bulk{suffix}',
                last_name='User',
                is_admin=False
            )
            users.append(user)

            prestation = Prestation(name=f'Service {i}')
            prestations.append(prestation)

        self.save_to_db(*users, *prestations)

        # Test récupération utilisateurs
        start_time = time.time()
        response = self.client.get('/users/')
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        duration = end_time - start_time

        # Récupération en moins de 2 secondes
        self.assertLess(duration, 2.0, f"Récupération utilisateurs trop lente: {duration:.2f}s")

    def test_database_query_performance(self):
        """Test performance des requêtes base de données"""
        # Créer données de test
        prestation = Prestation(name='Performance Test')
        users = []
        reviews = []

        for i in range(15):
            suffix = self._get_suffix(i)
            user = User(
                email=f'perf{i}@test.com',
                password='Password123!',
                first_name=f'Perf{suffix}',
                last_name='User',
                is_admin=False
            )
            users.append(user)

            review = Review(
                text=f'Avis performance {i}',
                rating=5,
                user=user,
                prestation=prestation
            )
            reviews.append(review)

        self.save_to_db(prestation, *users, *reviews)

        # Test requête complexe
        start_time = time.time()
        response = self.client.get('/reviews/public-reviews')
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        duration = end_time - start_time

        # Requête complexe en moins de 1.5 secondes
        self.assertLess(duration, 1.5, f"Requête reviews trop lente: {duration:.2f}s")

if __name__ == '__main__':
    unittest.main()
