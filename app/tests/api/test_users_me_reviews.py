#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review

class TestUsersMeReviewsAPI(BaseTest):
    """Tests API users me reviews - Tests pour /users/me/reviews"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.client = self.app.test_client()

        # Créer utilisateurs
        self.user = User(
            email='user@test.com',
            password='Password123!',
            first_name='User',
            last_name='Test',
            is_admin=False
        )
        self.other_user = User(
            email='other@test.com',
            password='Password123!',
            first_name='Other',
            last_name='User',
            is_admin=False
        )
        self.save_to_db(self.user, self.other_user)

        # Créer prestations
        self.prestation1 = Prestation(name='Massage')
        self.prestation2 = Prestation(name='Acupuncture')
        self.save_to_db(self.prestation1, self.prestation2)

        self.login_as_user()

    def login_as_user(self):
        credentials = {'email': 'user@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_user_reviews_success(self):
        """Test récupération des avis de l'utilisateur connecté"""
        # Créer avis pour l'utilisateur connecté
        review1 = Review(
            text='Excellent massage',
            rating=5,
            user=self.user,
            prestation=self.prestation1
        )
        review2 = Review(
            text='Bonne acupuncture',
            rating=4,
            user=self.user,
            prestation=self.prestation2
        )
        # Créer avis pour autre utilisateur (ne doit pas apparaître)
        review3 = Review(
            text='Avis autre utilisateur',
            rating=3,
            user=self.other_user,
            prestation=self.prestation1
        )
        self.save_to_db(review1, review2, review3)

        response = self.client.get('/users/me/reviews')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        
        ratings = [r['rating'] for r in response_data]
        self.assertIn(5, ratings)
        self.assertIn(4, ratings)
        self.assertNotIn(3, ratings)

    def test_get_user_reviews_empty(self):
        """Test récupération quand l'utilisateur n'a pas d'avis"""
        response = self.client.get('/users/me/reviews')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 0)

    def test_get_user_reviews_without_login(self):
        """Test récupération sans être connecté"""
        self.client.post('/auth/logout')
        response = self.client.get('/users/me/reviews')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()