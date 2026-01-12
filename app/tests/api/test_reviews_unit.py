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


class TestReviewsUnit(BaseTest):
    """Tests unitaires pour l'API reviews - Tests isolés de fonctionnalités spécifiques"""
    
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
        self.save_to_db(self.admin_user, self.regular_user)
        
        # Créer prestation
        self.prestation = Prestation(name='Test Prestation')
        self.save_to_db(self.prestation)
        
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

    
    def test_create_review_valid_data(self):
        """Test unitaire : création avec données valides"""
        
        valid_data = {
            'rating': 5,
            'text': 'Excellent service !',
            'prestation_id': str(self.prestation.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        
        if response.status_code != 201:
            debug_info = f"POST /reviews/ failed with {response.status_code}: {response.data}"
            self.fail(debug_info)
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        
        # Vérifier la structure de la réponse
        required_fields = ['id', 'rating', 'text', 'prestation_id']
        for field in required_fields:
            self.assertIn(field, response_data)
        
        # Vérifier les valeurs
        self.assertEqual(response_data['rating'], 5)
        self.assertEqual(response_data['text'], 'Excellent service !')
        self.assertEqual(response_data['prestation_id'], str(self.prestation.id))
    
    def test_create_review_missing_fields(self):
        """Test unitaire : création avec champs manquants"""
        
        incomplete_data_sets = [
            {'rating': 5, 'text': 'Test'},  # Manque prestation_id
            {'rating': 5, 'prestation_id': str(self.prestation.id)},  # Manque text
            {'text': 'Test', 'prestation_id': str(self.prestation.id)},  # Manque rating
            {'rating': 5},  # Manque text et prestation_id
            {'text': 'Test'},  # Manque rating et prestation_id
            {'prestation_id': str(self.prestation.id)},  # Manque rating et text
        ]
        
        for incomplete_data in incomplete_data_sets:
            response = self.client.post(
                '/reviews/',
                data=json.dumps(incomplete_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400,
                           f"Should reject incomplete data: {incomplete_data}")
    
    def test_create_review_invalid_rating_values(self):
        """Test unitaire : validation des valeurs de rating"""
        
        invalid_ratings = [
            (0, "Rating 0 should be invalid"),
            (6, "Rating 6 should be invalid"),
            (-1, "Negative rating should be invalid"),
            (100, "Rating 100 should be invalid"),
        ]
        
        for invalid_rating, message in invalid_ratings:
            data = {
                'rating': invalid_rating,
                'text': 'Test text',
                'prestation_id': str(self.prestation.id)
            }
            
            response = self.client.post(
                '/reviews/',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400, message)
    
    def test_create_review_valid_rating_values(self):
        """Test unitaire : validation des valeurs de rating valides"""
        
        valid_ratings = [1, 2, 3, 4, 5]
        
        for i, valid_rating in enumerate(valid_ratings):
            # Créer une nouvelle prestation pour chaque test
            prestation = Prestation(name=f'Prestation {i}')
            self.save_to_db(prestation)
            
            data = {
                'rating': valid_rating,
                'text': f'Test text for rating {valid_rating}',
                'prestation_id': str(prestation.id)
            }
            
            response = self.client.post(
                '/reviews/',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 201,
                           f"Rating {valid_rating} should be valid")
    
    def test_create_review_text_length_validation(self):
        """Test unitaire : validation de la longueur du texte"""
        
        # Texte minimum valide (2 caractères)
        min_valid_data = {
            'rating': 5,
            'text': 'OK',  # 2 caractères
            'prestation_id': str(self.prestation.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(min_valid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Nettoyer
        review_id = json.loads(response.data)['id']
        self.login_as_admin()
        self.client.delete(f'/reviews/{review_id}')
        self.login_as_regular_user()
        
        # Texte maximum valide (500 caractères)
        max_valid_text = 'A' * 500
        max_valid_data = {
            'rating': 5,
            'text': max_valid_text,
            'prestation_id': str(self.prestation.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(max_valid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
    
    def test_get_user_reviews_response_structure(self):
        """Test unitaire : structure de la réponse pour les commentaires utilisateur"""
        
        # Créer un commentaire
        review = Review(
            text='Test review',
            rating=4,
            user=self.regular_user,
            prestation=self.prestation
        )
        self.save_to_db(review)
        
        response = self.client.get('/reviews/me')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Vérifier que c'est une liste
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 1)
        
        # Vérifier la structure du commentaire (modèle utilisateur)
        review_data = response_data[0]
        user_fields = ['id', 'rating', 'text', 'prestation_id']
        
        for field in user_fields:
            self.assertIn(field, review_data)
        
        # Vérifier que user_id n'est PAS présent (modèle utilisateur)
        self.assertNotIn('user_id', review_data)
    
    def test_get_all_reviews_admin_response_structure(self):
        """Test unitaire : structure de la réponse admin pour tous les commentaires"""
        self.login_as_admin()
        
        # Créer un commentaire
        review = Review(
            text='Test review',
            rating=4,
            user=self.regular_user,
            prestation=self.prestation
        )
        self.save_to_db(review)
        
        response = self.client.get('/reviews/')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Vérifier que c'est une liste
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 1)
        
        # Vérifier la structure du commentaire (modèle admin)
        review_data = response_data[0]
        admin_fields = ['id', 'rating', 'text']
        
        for field in admin_fields:
            self.assertIn(field, review_data)
        
        # Vérifier les objets imbriqués
        self.assertIn('user', review_data)
        self.assertIn('prestation', review_data)
        self.assertIn('id', review_data['user'])
        self.assertIn('id', review_data['prestation'])
    
    def test_update_review_partial_data(self):
        """Test unitaire : mise à jour avec données partielles"""
        
        # Créer un commentaire
        review = Review(
            text='Original text',
            rating=3,
            user=self.regular_user,
            prestation=self.prestation
        )
        self.save_to_db(review)
        
        # Test 1: Modifier seulement le rating
        update_rating_only = {'rating': 5}
        
        response = self.client.patch(
            f'/reviews/{review.id}',
            data=json.dumps(update_rating_only),
            content_type='application/json'
        )
        
        if response.status_code != 200:
            error_data = response.data.decode('utf-8') if response.data else 'No error data'
            self.fail(f"PATCH failed with {response.status_code}: {error_data}")
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['rating'], 5)
        self.assertEqual(response_data['text'], 'Original text')  # Inchangé
        
        # Test 2: Modifier seulement le texte
        update_text_only = {'text': 'Updated text'}
        
        response = self.client.patch(
            f'/reviews/{review.id}',
            data=json.dumps(update_text_only),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['rating'], 5)  # Inchangé depuis la première mise à jour
        self.assertEqual(response_data['text'], 'Updated text')
    
    def test_update_review_empty_data(self):
        """Test unitaire : mise à jour avec données vides"""
        
        # Créer un commentaire
        review = Review(
            text='Original text',
            rating=3,
            user=self.regular_user,
            prestation=self.prestation
        )
        self.save_to_db(review)
        
        # Tenter une mise à jour avec données vides
        empty_data = {}
        
        response = self.client.patch(
            f'/reviews/{review.id}',
            data=json.dumps(empty_data),
            content_type='application/json'
        )
        
        # Devrait être accepté (pas de changement) ou rejeté selon la logique métier
        self.assertIn(response.status_code, [200, 400])
    
    def test_delete_review_response_format(self):
        """Test unitaire : format de la réponse de suppression"""
        self.login_as_admin()
        
        # Créer un commentaire
        review = Review(
            text='To be deleted',
            rating=3,
            user=self.regular_user,
            prestation=self.prestation
        )
        self.save_to_db(review)
        
        response = self.client.delete(f'/reviews/{review.id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Vérifier la structure de la réponse
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Commentaire supprimé avec succès')
    
    def test_nonexistent_review_operations(self):
        """Test unitaire : opérations sur des commentaires inexistants"""
        self.login_as_admin()
        
        fake_id = '00000000-0000-0000-0000-000000000000'
        
        # GET commentaire inexistant
        response = self.client.get(f'/reviews/{fake_id}')
        self.assertEqual(response.status_code, 404)
        
        # PATCH commentaire inexistant
        self.login_as_regular_user()
        
        response = self.client.patch(
            f'/reviews/{fake_id}',
            data=json.dumps({'rating': 5}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        
        # DELETE commentaire inexistant
        self.login_as_admin()
        
        response = self.client.delete(f'/reviews/{fake_id}')
        self.assertEqual(response.status_code, 404)
    
    def test_content_type_validation(self):
        """Test unitaire : validation du Content-Type"""
        
        valid_data = {
            'rating': 5,
            'text': 'Test',
            'prestation_id': str(self.prestation.id)
        }
        
        # Sans Content-Type
        response = self.client.post(
            '/reviews/',
            data=json.dumps(valid_data)
            # Pas de content_type
        )
        
        # Devrait échouer ou traiter différemment
        self.assertIn(response.status_code, [400, 415])
        
        # Avec mauvais Content-Type
        response = self.client.post(
            '/reviews/',
            data=json.dumps(valid_data),
            content_type='text/plain'
        )
        
        # Devrait échouer
        self.assertIn(response.status_code, [400, 415])


if __name__ == '__main__':
    unittest.main()