#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.reviews import api as reviews_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review

class TestReviewsByUserAPI(BaseTest):
    """Tests API reviews by user - Tests pour /reviews/by-user/<user_id>"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(reviews_api, path='/reviews')
        self.client = self.app.test_client()

        # Créer utilisateurs
        self.admin_user = User(
            email='admin@test.com',
            password='Password123!',
            first_name='Admin',
            last_name='Test',
            is_admin=True
        )
        self.user1 = User(
            email='user1@test.com',
            password='Password123!',
            first_name='Marie',
            last_name='Test',
            is_admin=False
        )
        self.user2 = User(
            email='user2@test.com',
            password='Password123!',
            first_name='Pierre',
            last_name='Test',
            is_admin=False
        )
        self.save_to_db(self.admin_user, self.user1, self.user2)

        # Créer prestations
        self.prestation1 = Prestation(name='Massage')
        self.prestation2 = Prestation(name='Acupuncture')
        self.save_to_db(self.prestation1, self.prestation2)

        self.login_as_admin()

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def login_as_user(self):
        credentials = {'email': 'user1@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_reviews_by_user_success(self):
        """Test récupération des avis par utilisateur spécifique"""
        # Créer avis pour user1
        review1 = Review(
            text='Avis Marie - 1',
            rating=5,
            user=self.user1,
            prestation=self.prestation1
        )
        review2 = Review(
            text='Avis Marie - 2',
            rating=4,
            user=self.user1,
            prestation=self.prestation2
        )
        # Créer avis pour user2 (ne doit pas apparaître)
        review3 = Review(
            text='Avis Pierre',
            rating=3,
            user=self.user2,
            prestation=self.prestation1
        )
        self.save_to_db(review1, review2, review3)

        response = self.client.get(f'/reviews/by-user/{self.user1.id}')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        
        # Vérifier que tous les avis appartiennent à user1
        for review in response_data:
            self.assertEqual(review['user']['id'], str(self.user1.id))

    def test_get_reviews_by_user_not_found(self):
        """Test avec utilisateur inexistant"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(f'/reviews/by-user/{fake_id}')
        self.assertEqual(response.status_code, 404)

    def test_get_reviews_by_user_empty(self):
        """Test utilisateur sans avis"""
        response = self.client.get(f'/reviews/by-user/{self.user1.id}')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 0)

    def test_get_reviews_by_user_requires_admin(self):
        """Test que l'endpoint nécessite des droits admin"""
        self.login_as_user()
        response = self.client.get(f'/reviews/by-user/{self.user1.id}')
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()