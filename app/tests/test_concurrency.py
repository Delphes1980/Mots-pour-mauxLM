#!/usr/bin/env python3

import json
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api
from app.api.v1.reviews import api as reviews_api
from app.models.user import User
from app.models.prestation import Prestation

class TestConcurrency(BaseTest):
    """Tests de concurrence - Accès simultané aux ressources"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.api.add_namespace(reviews_api, path='/reviews')
        self.client = self.app.test_client()

        # Créer prestation pour les tests
        self.prestation = Prestation(name='Concurrent Test')
        self.save_to_db(self.prestation)

    def _get_suffix(self, index):
        """Helper pour générer des suffixes alphabétiques (0->A, 1->B...)"""
        return chr(65 + index)

    def test_concurrent_user_creation(self):
        """Test création simultanée d'utilisateurs"""
        results = []
        app = self.app

        def create_user(index):
            with app.app_context():
                client = self.app.test_client()
                suffix = self._get_suffix(index)
                data = {
                    'first_name': f'Concurrent{suffix}',
                    'last_name': 'User',
                    'email': f'concurrent{index}@test.com',
                    'password': 'Password123!'
                }
                response = client.post('/users/', data=json.dumps(data), content_type='application/json')
                results.append(response.status_code)

        # Lancer 5 créations simultanées
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_user, args=(i,))
            threads.append(thread)
            thread.start()

        # Attendre la fin de tous les threads
        for thread in threads:
            thread.join()

        # Tous devraient réussir
        success_count = sum(1 for status in results if status == 201)
        self.assertEqual(success_count, 5, f"Seulement {success_count}/5 créations ont réussi")

    def test_concurrent_login_attempts(self):
        """Test connexions simultanées du même utilisateur"""
        # Créer utilisateur
        user = User(
            email='concurrent@test.com',
            password='Password123!',
            first_name='Concurrent',
            last_name='User',
            is_admin=False
        )
        self.save_to_db(user)

        results = []

        def login_user():
            client = self.app.test_client()
            credentials = {'email': 'concurrent@test.com', 'password': 'Password123!'}
            response = client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
            results.append(response.status_code)

        # Lancer 3 connexions simultanées
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(login_user) for _ in range(3)]
            for future in futures:
                future.result()

        # Toutes devraient réussir
        success_count = sum(1 for status in results if status == 200)
        self.assertEqual(success_count, 3, f"Seulement {success_count}/3 connexions ont réussi")

    def test_concurrent_review_creation(self):
        """Test création simultanée d'avis par différents utilisateurs"""
        # Créer utilisateurs
        users = []
        for i in range(3):
            suffix = self._get_suffix(i)
            user = User(
                email=f'reviewer{i}@test.com',
                password='Password123!',
                first_name=f'Reviewer{suffix}',
                last_name='User',
                is_admin=False
            )
            users.append(user)
        self.save_to_db(*users)

        results = []
        app = self.app
        prestation_id_str = str(self.prestation.id)

        def create_review(user_email, index):
            with app.app_context():
                client = self.app.test_client()

                # Login
                credentials = {'email': user_email, 'password': 'Password123!'}
                client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')

                # Créer avis
                review_data = {
                    'rating': 5,
                    'text': f'Avis concurrent {index}',
                    'prestation_id': str(self.prestation.id)
                }
                response = client.post('/reviews/', data=json.dumps(review_data), content_type='application/json')
                results.append(response.status_code)

        # Lancer créations simultanées
        threads = []
        for i, user in enumerate(users):
            thread = threading.Thread(target=create_review, args=(user.email, i))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Tous devraient réussir
        success_count = sum(1 for status in results if status == 201)
        self.assertEqual(success_count, 3, f"Seulement {success_count}/3 avis créés")

    def test_race_condition_duplicate_email(self):
        """Test race condition sur email unique"""
        results = []
        app = self.app

        def create_duplicate_user(index):
            with app.app_context():
                client = self.app.test_client()
                suffix = self._get_suffix(index)
                data = {
                    'first_name': f'Race{suffix}',
                    'last_name': 'User',
                    'email': 'race@test.com',  # Même email
                    'password': 'Password123!'
                }
                response = client.post('/users/', data=json.dumps(data), content_type='application/json')
                results.append(response.status_code)

        # Lancer 3 créations simultanées avec même email
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_duplicate_user, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Un seul devrait réussir, les autres échouer
        success_count = sum(1 for status in results if status == 201)
        error_count = sum(1 for status in results if status != 201)

        self.assertEqual(success_count, 1, f"Devrait avoir 1 succès, eu {success_count}")
        self.assertEqual(error_count, 2, f"Devrait avoir 2 erreurs, eu {error_count}")

    def test_concurrent_data_access(self):
        """Test accès concurrent aux mêmes données"""
        # Créer admin
        admin = User(
            email='admin@test.com',
            password='Password123!',
            first_name='Admin',
            last_name='Test',
            is_admin=True
        )
        self.save_to_db(admin)

        results = []
        app = self.app

        def access_users():
            with app.app_context():
                client = self.app.test_client()

                # Login admin
                credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
                client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')

                # Accéder aux utilisateurs
                response = client.get('/users/')
                results.append(response.status_code)

        # Lancer 4 accès simultanés
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(access_users) for _ in range(4)]
            for future in futures:
                future.result()

        # Tous devraient réussir
        success_count = sum(1 for status in results if status == 200)
        self.assertEqual(success_count, 4, f"Seulement {success_count}/4 accès ont réussi")

if __name__ == '__main__':
    unittest.main()
