#!/usr/bin/env python3

import json
import unittest
from flask_jwt_extended import create_access_token

from app.tests.base_test import BaseTest
from app.api.v1.reviews import api as reviews_api
from app.api.v1.authentication import api as auth_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.appointment import Appointment


class TestReviewsIntegration(BaseTest):
    """Tests d'intégration pour l'API reviews - Scénarios complets"""
    
    def test_base_is_clean(self):
        self.tearDown()
        users = User.query.all()
        prestations = Prestation.query.all()
        reviews = Review.query.all()
        appointments = Appointment.query.all()
        self.assertEqual(len(users), 0)
        self.assertEqual(len(prestations), 0)
        self.assertEqual(len(reviews), 0)
        self.assertEqual(len(appointments), 0)
        self.setUp()

    def setUp(self):
        super().setUp()
        
        # Configuration de l'API via BaseTest
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(reviews_api, path='/reviews')
        
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
        self.user1 = User(
            email='user1@test.com',
            password='Password123!',
            first_name='Alice',
            last_name='Test',
            is_admin=False
        )
        self.user2 = User(
            email='user2@test.com',
            password='Password123!',
            first_name='Bob',
            last_name='Test',
            is_admin=False
        )
        self.save_to_db(self.admin_user, self.user1, self.user2)
        
        # Créer prestations
        self.prestation1 = Prestation(name='Massage Thérapeutique')
        self.prestation2 = Prestation(name='Acupuncture')
        self.prestation3 = Prestation(name='Réflexologie')
        self.save_to_db(self.prestation1, self.prestation2, self.prestation3)

    def login_as_user(self, user_email, password):
        """Se connecter en tant qu'utilisateur et garder les cookies"""
        credentials = {
            'email': user_email,
            'password': password
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        return response.status_code == 200
    
    def test_complete_review_workflow(self):
        """Test du workflow complet : création -> lecture -> modification -> suppression"""
        # 1. Connexion utilisateur
        self.assertTrue(self.login_as_user('user1@test.com', 'Password123!'))
        
        # 2. Création d'un commentaire
        review_data = {
            'rating': 4,
            'text': 'Très bon massage, je recommande !',
            'prestation_id': str(self.prestation1.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        created_review = json.loads(response.data)
        review_id = created_review['id']
        
        # 3. Lecture du commentaire créé
        response = self.client.get('/reviews/me')
        self.assertEqual(response.status_code, 200)
        user_reviews = json.loads(response.data)
        self.assertEqual(len(user_reviews), 1)
        self.assertEqual(user_reviews[0]['rating'], 4)
        
        # 4. Modification du commentaire
        update_data = {
            'rating': 5,
            'text': 'Excellent massage, parfait !'
        }
        
        response = self.client.patch(
            f'/reviews/{review_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        updated_review = json.loads(response.data)
        self.assertEqual(updated_review['rating'], 5)
        self.assertEqual(updated_review['text'], 'Excellent massage, parfait !')
        
        # 5. Vérification de la modification
        response = self.client.get('/reviews/me')
        user_reviews = json.loads(response.data)
        self.assertEqual(user_reviews[0]['rating'], 5)
        
        # 6. Suppression par admin
        self.assertTrue(self.login_as_user('admin@test.com', 'Password123!'))
        
        response = self.client.delete(f'/reviews/{review_id}')
        self.assertEqual(response.status_code, 200)
        
        # 7. Vérification de la suppression
        response = self.client.get(f'/reviews/{review_id}')
        self.assertEqual(response.status_code, 404)
    
    def test_multiple_users_multiple_prestations(self):
        """Test avec plusieurs utilisateurs et prestations"""
        # User1 crée des commentaires
        self.assertTrue(self.login_as_user('user1@test.com', 'Password123!'))
        
        reviews_user1 = [
            {
                'rating': 5,
                'text': 'Excellent massage !',
                'prestation_id': str(self.prestation1.id)
            },
            {
                'rating': 4,
                'text': 'Bonne séance d\'acupuncture',
                'prestation_id': str(self.prestation2.id)
            }
        ]
        
        for review_data in reviews_user1:
            response = self.client.post(
                '/reviews/',
                data=json.dumps(review_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
        
        # User2 crée des commentaires
        self.assertTrue(self.login_as_user('user2@test.com', 'Password123!'))
        
        reviews_user2 = [
            {
                'rating': 3,
                'text': 'Correct mais peut mieux faire',
                'prestation_id': str(self.prestation1.id)
            },
            {
                'rating': 5,
                'text': 'Réflexologie parfaite !',
                'prestation_id': str(self.prestation3.id)
            }
        ]
        
        for review_data in reviews_user2:
            response = self.client.post(
                '/reviews/',
                data=json.dumps(review_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
        
        # Admin vérifie tous les commentaires
        self.assertTrue(self.login_as_user('admin@test.com', 'Password123!'))
        
        response = self.client.get('/reviews/')
        self.assertEqual(response.status_code, 200)
        all_reviews = json.loads(response.data)
        self.assertEqual(len(all_reviews), 4)
        
        # Vérifier les commentaires par prestation
        response = self.client.get(f'/reviews/prestation/{self.prestation1.id}')
        self.assertEqual(response.status_code, 200)
        prestation1_reviews = json.loads(response.data)
        self.assertEqual(len(prestation1_reviews), 2)  # User1 et User2
        
        # Vérifier les commentaires par utilisateur et prestation
        response = self.client.get(f'/reviews/user/{self.user1.id}/prestation/{self.prestation1.id}')
        self.assertEqual(response.status_code, 200)
        specific_review = json.loads(response.data)
        
        if isinstance(specific_review, list):
            self.assertEqual(len(specific_review), 1)
            self.assertEqual(specific_review[0]['text'], 'Excellent massage !')
        else:
            self.assertEqual(specific_review['text'], 'Excellent massage !')
    
    def test_review_constraints_and_validations(self):
        """Test des contraintes et validations métier"""
        self.assertTrue(self.login_as_user('user1@test.com', 'Password123!'))
        
        # 1. Créer un premier commentaire
        review_data = {
            'rating': 4,
            'text': 'Premier commentaire',
            'prestation_id': str(self.prestation1.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # 2. Tenter de créer un second commentaire pour la même prestation
        duplicate_review = {
            'rating': 5,
            'text': 'Tentative de doublon',
            'prestation_id': str(self.prestation1.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(duplicate_review),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 409)
        
        # 3. Créer un commentaire pour une autre prestation (devrait marcher)
        other_review = {
            'rating': 3,
            'text': 'Commentaire pour autre prestation',
            'prestation_id': str(self.prestation2.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(other_review),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # 4. Vérifier que l'utilisateur a bien 2 commentaires
        response = self.client.get('/reviews/me')
        user_reviews = json.loads(response.data)
        self.assertEqual(len(user_reviews), 2)
    
    def test_cross_user_permissions(self):
        """Test des permissions entre utilisateurs"""
        # User1 crée un commentaire
        self.assertTrue(self.login_as_user('user1@test.com', 'Password123!'))
        
        review_data = {
            'rating': 4,
            'text': 'Commentaire de User1',
            'prestation_id': str(self.prestation1.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        review_id = json.loads(response.data)['id']
        
        # User2 tente de modifier le commentaire de User1
        self.assertTrue(self.login_as_user('user2@test.com', 'Password123!'))
        
        update_data = {
            'rating': 1,
            'text': 'Tentative de modification malveillante'
        }
        
        response = self.client.patch(
            f'/reviews/{review_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        
        # User2 tente de supprimer le commentaire de User1
        response = self.client.delete(f'/reviews/{review_id}')
        self.assertEqual(response.status_code, 403)
        
        # Admin peut supprimer n'importe quel commentaire
        self.assertTrue(self.login_as_user('admin@test.com', 'Password123!'))
        
        response = self.client.delete(f'/reviews/{review_id}')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_management_workflow(self):
        """Test du workflow de gestion admin"""
        # Créer des commentaires avec différents utilisateurs
        users_and_reviews = [
            (self.user1, 'user1@test.com', 'Commentaire User1'),
            (self.user2, 'user2@test.com', 'Commentaire User2')
        ]
        
        created_reviews = []
        
        for user, email, text in users_and_reviews:
            self.assertTrue(self.login_as_user(email, 'Password123!'))
            
            review_data = {
                'rating': 4,
                'text': text,
                'prestation_id': str(self.prestation1.id)
            }
            
            response = self.client.post(
                '/reviews/',
                data=json.dumps(review_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
            created_reviews.append(json.loads(response.data)['id'])
        
        # Admin se connecte et gère les commentaires
        self.assertTrue(self.login_as_user('admin@test.com', 'Password123!'))
        
        # 1. Voir tous les commentaires
        response = self.client.get('/reviews/')
        self.assertEqual(response.status_code, 200)
        all_reviews = json.loads(response.data)
        self.assertEqual(len(all_reviews), 2)
        
        # 2. Voir les commentaires par prestation
        response = self.client.get(f'/reviews/prestation/{self.prestation1.id}')
        self.assertEqual(response.status_code, 200)
        prestation_reviews = json.loads(response.data)
        self.assertEqual(len(prestation_reviews), 2)
        
        # 3. Voir un commentaire spécifique
        response = self.client.get(f'/reviews/{created_reviews[0]}')
        self.assertEqual(response.status_code, 200)
        specific_review = json.loads(response.data)
        self.assertIn('user_id', specific_review)  # Modèle admin
        
        # 4. Supprimer un commentaire
        response = self.client.delete(f'/reviews/{created_reviews[0]}')
        self.assertEqual(response.status_code, 200)
        
        # 5. Vérifier la suppression
        response = self.client.get('/reviews/')
        remaining_reviews = json.loads(response.data)
        self.assertEqual(len(remaining_reviews), 1)


if __name__ == '__main__':
    unittest.main()