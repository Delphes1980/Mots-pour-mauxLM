#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api
from app.api.v1.appointments import api as appointments_api
from app.api.v1.reviews import api as reviews_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment
from app.models.review import Review

class TestEndToEndWorkflow(BaseTest):
    """Tests end-to-end complets - Workflow utilisateur complet"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.api.add_namespace(appointments_api, path='/appointments')
        self.api.add_namespace(reviews_api, path='/reviews')
        self.client = self.app.test_client()

        # Créer prestation
        self.prestation = Prestation(name='Massage Thérapeutique')
        self.save_to_db(self.prestation)

    def test_complete_user_workflow(self):
        """Test workflow complet : création utilisateur → appointment → avis"""
        
        # 1. Créer un utilisateur
        user_data = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'jean.dupont@example.com',
            'password': 'Password123!',
            'address': '123 Rue de la Paix',
            'phone_number': '0123456789'
        }
        
        response = self.client.post(
            '/users/',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        user_response = json.loads(response.data)
        user_id = user_response['id']
        
        # 2. Se connecter
        login_data = {
            'email': 'jean.dupont@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 3. Créer un rendez-vous
        appointment_data = {
            'message': 'Je souhaite un massage pour des douleurs dorsales.',
            'prestation_id': str(self.prestation.id)
        }
        response = self.client.post(
            '/appointments/',
            data=json.dumps(appointment_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        appointment_response = json.loads(response.data)
        
        # 4. Créer un avis
        review_data = {
            'rating': 5,
            'text': 'Excellent massage, très professionnel. Je recommande vivement !',
            'prestation_id': str(self.prestation.id)
        }
        response = self.client.post(
            '/reviews/',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        review_response = json.loads(response.data)
        
        # 5. Vérifier les données utilisateur
        response = self.client.get('/users/me')
        self.assertEqual(response.status_code, 200)
        me_response = json.loads(response.data)
        self.assertEqual(me_response['email'], 'jean.dupont@example.com')
        self.assertEqual(me_response['first_name'], 'Jean')
        
        # 6. Vérifier les avis de l'utilisateur
        response = self.client.get('/users/me/reviews')
        self.assertEqual(response.status_code, 200)
        reviews_response = json.loads(response.data)
        self.assertEqual(len(reviews_response), 1)
        self.assertEqual(reviews_response[0]['rating'], 5)
        
        # 7. Vérifier que l'avis apparaît dans les avis publics
        response = self.client.get('/reviews/public-reviews')
        self.assertEqual(response.status_code, 200)
        public_reviews = json.loads(response.data)
        self.assertEqual(len(public_reviews), 1)
        self.assertEqual(public_reviews[0]['user']['first_name'], 'Jean')

    def test_admin_workflow(self):
        """Test workflow admin : création utilisateur par admin → gestion"""
        
        # 1. Créer admin
        admin_user = User(
            email='admin@test.com',
            password='Password123!',
            first_name='Admin',
            last_name='Test',
            is_admin=True
        )
        self.save_to_db(admin_user)
        
        # 2. Se connecter en tant qu'admin
        login_data = {
            'email': 'admin@test.com',
            'password': 'Password123!'
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 3. Créer utilisateur via admin
        user_data = {
            'first_name': 'Marie',
            'last_name': 'Martin',
            'email': 'marie.martin@example.com'
        }
        response = self.client.post(
            '/users/admin-create',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # 4. Récupérer tous les utilisateurs
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)
        users_response = json.loads(response.data)
        self.assertEqual(len(users_response), 2)  # Admin + Marie
        
        # 5. Rechercher utilisateur par email
        response = self.client.get('/users/search?email=marie.martin@example.com')
        self.assertEqual(response.status_code, 200)
        search_response = json.loads(response.data)
        self.assertEqual(search_response['first_name'], 'Marie')

if __name__ == '__main__':
    unittest.main()