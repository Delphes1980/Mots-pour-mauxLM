#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.reviews import api as reviews_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review

class TestPublicReviewsAPI(BaseTest):
    """Tests API public reviews - Tests pour /reviews/public-reviews"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(reviews_api, path='/reviews')
        self.client = self.app.test_client()

        # Créer utilisateurs
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
        self.save_to_db(self.user1, self.user2)

        # Créer prestations
        self.prestation1 = Prestation(name='Massage')
        self.prestation2 = Prestation(name='Acupuncture')
        self.save_to_db(self.prestation1, self.prestation2)

    def test_get_public_reviews_success(self):
        """Test récupération des avis publics"""
        # Créer avis publics
        review1 = Review(
            text='Excellent service',
            rating=5,
            user=self.user1,
            prestation=self.prestation1
        )
        review2 = Review(
            text='Très satisfait',
            rating=4,
            user=self.user2,
            prestation=self.prestation2
        )
        self.save_to_db(review1, review2)

        response = self.client.get('/reviews/public-reviews')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        
        # Vérifier structure des données publiques
        for review in response_data:
            self.assertIn('id', review)
            self.assertIn('rating', review)
            self.assertIn('text', review)
            self.assertIn('user', review)
            self.assertIn('first_name', review['user'])
            self.assertIn('last_name', review['user'])

    def test_get_public_reviews_empty(self):
        """Test récupération quand aucun avis"""
        response = self.client.get('/reviews/public-reviews')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 0)

    def test_get_public_reviews_no_auth_required(self):
        """Test que l'endpoint public ne nécessite pas d'authentification"""
        # Créer un avis
        review = Review(
            text='Avis public',
            rating=5,
            user=self.user1,
            prestation=self.prestation1
        )
        self.save_to_db(review)

        # Pas de login nécessaire
        response = self.client.get('/reviews/public-reviews')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)

if __name__ == '__main__':
    unittest.main()