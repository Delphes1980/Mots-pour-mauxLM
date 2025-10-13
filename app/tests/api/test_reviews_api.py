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


class TestReviewsAPI(BaseTest):
    """Tests API reviews - Tests de bout en bout avec vraie DB"""
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
        self.regular_user = User(
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
        self.save_to_db(self.admin_user, self.regular_user, self.other_user)
        
        # Créer prestations
        self.prestation1 = Prestation(name='Massage Thérapeutique')
        self.prestation2 = Prestation(name='Acupuncture')
        self.save_to_db(self.prestation1, self.prestation2)
        
        # Se connecter par défaut en tant qu'utilisateur régulier
        self.login_as_regular_user()

    def login_as_regular_user(self):
        """Se connecter en tant qu'utilisateur régulier et garder les cookies"""
        credentials = {
            'email': 'user@test.com',
            'password': 'Password123!'
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def login_as_admin(self):
        """Se connecter en tant qu'admin et garder les cookies"""
        credentials = {
            'email': 'admin@test.com',
            'password': 'Password123!'
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def login_as_other_user(self):
        """Se connecter en tant qu'autre utilisateur et garder les cookies"""
        credentials = {
            'email': 'other@test.com',
            'password': 'Password123!'
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_create_review_success(self):
        """Test création réussie d'un commentaire"""
        
        data = {
            'rating': 5,
            'text': 'Excellent massage, très relaxant !',
            'prestation_id': str(self.prestation1.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['rating'], 5)
        self.assertEqual(response_data['text'], 'Excellent massage, très relaxant !')
        self.assertEqual(response_data['prestation_id'], str(self.prestation1.id))
        self.assertIn('id', response_data)
        
        # Vérifier en DB
        review = Review.query.filter_by(user_id=self.regular_user.id).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
    
    def test_create_review_duplicate(self):
        """Test création commentaire en double pour même prestation"""
        self.login_as_regular_user()
        
        # Créer premier commentaire
        data = {
            'rating': 4,
            'text': 'Premier commentaire',
            'prestation_id': str(self.prestation1.id)
        }
        response = self.client.post(
            '/reviews/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Tenter de créer un second commentaire pour la même prestation
        data2 = {
            'rating': 5,
            'text': 'Second commentaire',
            'prestation_id': str(self.prestation1.id)
        }
        response = self.client.post(
            '/reviews/',
            data=json.dumps(data2),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 409)
        response_data = json.loads(response.data)
        self.assertIn('existe déjà', response_data['error'])
    
    def test_create_review_invalid_prestation(self):
        """Test création avec prestation inexistante"""
        self.login_as_regular_user()
        
        fake_id = '00000000-0000-0000-0000-000000000000'
        data = {
            'rating': 5,
            'text': 'Commentaire test',
            'prestation_id': fake_id
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_create_review_invalid_data(self):
        """Test création avec données invalides"""
        self.login_as_regular_user()
        
        invalid_data_sets = [
            {},  # Pas de données
            {'rating': 5},  # Manque text et prestation_id
            {'text': 'Test'},  # Manque rating et prestation_id
            {'rating': 0, 'text': 'Test', 'prestation_id': str(self.prestation1.id)},  # Rating invalide
            {'rating': 6, 'text': 'Test', 'prestation_id': str(self.prestation1.id)},  # Rating invalide
            {'rating': 5, 'text': 'X', 'prestation_id': str(self.prestation1.id)},  # Text trop court
            {'rating': 5, 'text': 'X' * 501, 'prestation_id': str(self.prestation1.id)},  # Text trop long
        ]
        
        for data in invalid_data_sets:
            response = self.client.post(
                '/reviews/',
                data=json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)
    
    def test_create_review_without_login(self):
        """Test création sans être connecté"""
        # Déconnecter l'utilisateur
        self.client.post('/auth/logout')
        
        data = {
            'rating': 5,
            'text': 'Test commentaire',
            'prestation_id': str(self.prestation1.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_user_reviews_success(self):
        """Test récupération des commentaires de l'utilisateur connecté"""
        self.login_as_regular_user()
        
        # Créer quelques commentaires
        review1 = Review(
            text='Premier commentaire',
            rating=5,
            user=self.regular_user,
            prestation=self.prestation1
        )
        review2 = Review(
            text='Second commentaire',
            rating=4,
            user=self.regular_user,
            prestation=self.prestation2
        )
        self.save_to_db(review1, review2)
        
        response = self.client.get('/reviews/me')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        
        ratings = [r['rating'] for r in response_data]
        self.assertIn(5, ratings)
        self.assertIn(4, ratings)
    
    def test_get_user_reviews_empty(self):
        """Test récupération quand l'utilisateur n'a pas de commentaires"""
        self.login_as_regular_user()
        
        response = self.client.get('/reviews/me')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 0)
    
    def test_get_all_reviews_as_admin(self):
        """Test récupération de tous les commentaires en tant qu'admin"""
        self.login_as_admin()
        
        # Créer commentaires de différents utilisateurs
        review1 = Review(
            text='Commentaire user 1',
            rating=5,
            user=self.regular_user,
            prestation=self.prestation1
        )
        review2 = Review(
            text='Commentaire user 2',
            rating=3,
            user=self.other_user,
            prestation=self.prestation2
        )
        self.save_to_db(review1, review2)
        
        response = self.client.get('/reviews/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        
        # Vérifier que les user_id sont présents (modèle admin)
        for review in response_data:
            self.assertIn('user_id', review)
            self.assertIn('prestation_id', review)
    
    def test_get_all_reviews_as_regular_user(self):
        """Test récupération de tous les commentaires en tant qu'utilisateur normal"""
        self.login_as_regular_user()
        
        response = self.client.get('/reviews/')
        
        self.assertEqual(response.status_code, 403)
    
    def test_get_reviews_by_prestation_as_admin(self):
        """Test récupération des commentaires par prestation en tant qu'admin"""
        self.login_as_admin()
        
        # Créer commentaires pour une prestation spécifique
        review1 = Review(
            text='Commentaire 1',
            rating=5,
            user=self.regular_user,
            prestation=self.prestation1
        )
        review2 = Review(
            text='Commentaire 2',
            rating=4,
            user=self.other_user,
            prestation=self.prestation1
        )
        # Commentaire pour autre prestation
        review3 = Review(
            text='Autre prestation',
            rating=3,
            user=self.regular_user,
            prestation=self.prestation2
        )
        self.save_to_db(review1, review2, review3)
        
        response = self.client.get(f'/reviews/prestation/{self.prestation1.id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)  # Seulement les commentaires de prestation1
        
        for review in response_data:
            self.assertEqual(review['prestation_id'], str(self.prestation1.id))
    
    def test_get_review_by_id_as_admin(self):
        """Test récupération d'un commentaire par ID en tant qu'admin"""
        self.login_as_admin()
        
        review = Review(
            text='Commentaire test',
            rating=5,
            user=self.regular_user,
            prestation=self.prestation1
        )
        self.save_to_db(review)
        
        response = self.client.get(f'/reviews/{review.id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['rating'], 5)
        self.assertEqual(response_data['text'], 'Commentaire test')
        self.assertEqual(response_data['id'], str(review.id))
    
    def test_update_review_success(self):
        """Test mise à jour réussie d'un commentaire"""
        self.login_as_regular_user()
        
        # Créer un commentaire
        review = Review(
            text='Commentaire original',
            rating=3,
            user=self.regular_user,
            prestation=self.prestation1
        )
        self.save_to_db(review)
        
        # Mettre à jour
        update_data = {
            'rating': 5,
            'text': 'Commentaire mis à jour'
        }
        
        response = self.client.patch(
            f'/reviews/{review.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['rating'], 5)
        self.assertEqual(response_data['text'], 'Commentaire mis à jour')
        
        # Vérifier en DB
        self.db.session.expire_all()
        updated_review = Review.query.get(review.id)
        self.assertEqual(updated_review.rating, 5)
        self.assertEqual(updated_review.text, 'Commentaire mis à jour')
    
    def test_update_review_not_owner(self):
        """Test mise à jour d'un commentaire par un autre utilisateur"""
        self.login_as_other_user()
        
        # Créer un commentaire appartenant à regular_user
        review = Review(
            text='Commentaire original',
            rating=3,
            user=self.regular_user,
            prestation=self.prestation1
        )
        self.save_to_db(review)
        
        # Tenter de mettre à jour avec other_user
        update_data = {
            'rating': 5,
            'text': 'Tentative de modification'
        }
        
        response = self.client.patch(
            f'/reviews/{review.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_update_review_not_found(self):
        """Test mise à jour d'un commentaire inexistant"""
        self.login_as_regular_user()
        
        fake_id = '00000000-0000-0000-0000-000000000000'
        update_data = {
            'rating': 5,
            'text': 'Test'
        }
        
        response = self.client.patch(
            f'/reviews/{fake_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_delete_review_as_admin(self):
        """Test suppression d'un commentaire en tant qu'admin"""
        self.login_as_admin()
        
        review = Review(
            text='Commentaire à supprimer',
            rating=3,
            user=self.regular_user,
            prestation=self.prestation1
        )
        self.save_to_db(review)
        review_id = review.id
        
        response = self.client.delete(f'/reviews/{review_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Commentaire supprimé avec succès')
        
        # Vérifier suppression en DB
        self.db.session.expire_all()
        deleted_review = Review.query.get(review_id)
        self.assertIsNone(deleted_review)
    
    def test_delete_review_as_regular_user(self):
        """Test suppression d'un commentaire en tant qu'utilisateur normal"""
        self.login_as_regular_user()
        
        review = Review(
            text='Commentaire test',
            rating=3,
            user=self.regular_user,
            prestation=self.prestation1
        )
        self.save_to_db(review)
        
        response = self.client.delete(f'/reviews/{review.id}')
        
        self.assertEqual(response.status_code, 403)
    
    def test_get_reviews_by_user_and_prestation_as_admin(self):
        """Test récupération des commentaires par utilisateur et prestation"""
        self.login_as_admin()
        
        # Créer commentaire spécifique
        review = Review(
            text='Commentaire spécifique',
            rating=4,
            user=self.regular_user,
            prestation=self.prestation1
        )
        # Créer autre commentaire pour vérifier la spécificité
        other_review = Review(
            text='Autre commentaire',
            rating=3,
            user=self.other_user,
            prestation=self.prestation1
        )
        self.save_to_db(review, other_review)
        
        response = self.client.get(f'/reviews/user/{self.regular_user.id}/prestation/{self.prestation1.id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Devrait retourner seulement le commentaire du user spécifique
        if isinstance(response_data, list):
            self.assertEqual(len(response_data), 1)
            self.assertEqual(response_data[0]['text'], 'Commentaire spécifique')
        else:
            # Si c'est un seul objet
            self.assertEqual(response_data['text'], 'Commentaire spécifique')


if __name__ == '__main__':
    unittest.main()