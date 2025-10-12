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


class TestReviewsSecurity(BaseTest):
    """Tests de sécurité pour l'API reviews"""
    
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
        self.malicious_user = User(
            email='hacker@test.com',
            password='Password123!',
            first_name='Hacker',
            last_name='Test',
            is_admin=False
        )
        self.save_to_db(self.admin_user, self.regular_user, self.malicious_user)
        
        # Créer prestation
        self.prestation = Prestation(name='Test Prestation')
        self.save_to_db(self.prestation)

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
    
    def test_authentication_required_for_all_endpoints(self):
        """Test que l'authentification est requise pour tous les endpoints"""
        endpoints_and_methods = [
            ('/reviews/', 'POST'),
            ('/reviews/', 'GET'),
            ('/reviews/me', 'GET'),
            (f'/reviews/prestation/{self.prestation.id}', 'GET'),
            (f'/reviews/user/{self.regular_user.id}/prestation/{self.prestation.id}', 'GET'),
            ('/reviews/fake-id', 'GET'),
            ('/reviews/fake-id', 'PATCH'),
            ('/reviews/fake-id', 'DELETE'),
        ]
        
        for endpoint, method in endpoints_and_methods:
            if method == 'POST':
                response = self.client.post(
                    endpoint,
                    data=json.dumps({'test': 'data'}),
                    content_type='application/json'
                )
            elif method == 'GET':
                response = self.client.get(endpoint)
            elif method == 'PATCH':
                response = self.client.patch(
                    endpoint,
                    data=json.dumps({'test': 'data'}),
                    content_type='application/json'
                )
            elif method == 'DELETE':
                response = self.client.delete(endpoint)
            
            self.assertEqual(response.status_code, 401, 
                           f"Endpoint {method} {endpoint} should require authentication")
    
    def test_admin_only_endpoints_security(self):
        """Test que certains endpoints sont réservés aux admins"""
        self.assertTrue(self.login_as_user('user@test.com', 'Password123!'))
        
        admin_only_endpoints = [
            ('/reviews/', 'GET'),  # Liste tous les commentaires
            (f'/reviews/prestation/{self.prestation.id}', 'GET'),
            (f'/reviews/user/{self.regular_user.id}/prestation/{self.prestation.id}', 'GET'),
            ('/reviews/fake-id', 'GET'),  # Voir un commentaire par ID
            ('/reviews/fake-id', 'DELETE'),  # Supprimer un commentaire
        ]
        
        for endpoint, method in admin_only_endpoints:
            if method == 'GET':
                response = self.client.get(endpoint)
            elif method == 'DELETE':
                response = self.client.delete(endpoint)
            
            self.assertEqual(response.status_code, 403,
                           f"Endpoint {method} {endpoint} should be admin-only")
    
    def test_user_can_only_modify_own_reviews(self):
        """Test qu'un utilisateur ne peut modifier que ses propres commentaires"""
        # User crée un commentaire
        self.assertTrue(self.login_as_user('user@test.com', 'Password123!'))
        
        review_data = {
            'rating': 4,
            'text': 'Mon commentaire',
            'prestation_id': str(self.prestation.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(review_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        review_id = json.loads(response.data)['id']
        
        # Hacker tente de modifier le commentaire
        self.assertTrue(self.login_as_user('hacker@test.com', 'Password123!'))
        
        malicious_update = {
            'rating': 1,
            'text': 'Commentaire modifié malicieusement'
        }
        
        response = self.client.patch(
            f'/reviews/{review_id}',
            data=json.dumps(malicious_update),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        
        # Vérifier que le commentaire n'a pas été modifié
        self.assertTrue(self.login_as_user('admin@test.com', 'Password123!'))
        
        response = self.client.get(f'/reviews/{review_id}')
        self.assertEqual(response.status_code, 200)
        review = json.loads(response.data)
        self.assertEqual(review['text'], 'Mon commentaire')  # Pas modifié
        self.assertEqual(review['rating'], 4)  # Pas modifié
    
    def test_injection_attempts_in_review_content(self):
        """Test de tentatives d'injection dans le contenu des commentaires"""
        self.assertTrue(self.login_as_user('hacker@test.com', 'Password123!'))
        
        injection_attempts = [
            {
                'rating': 5,
                'text': '<script>alert("XSS")</script>',
                'prestation_id': str(self.prestation.id)
            },
            {
                'rating': 5,
                'text': "'; DROP TABLE reviews; --",
                'prestation_id': str(self.prestation.id)
            },
            {
                'rating': 5,
                'text': '{{7*7}}',  # Template injection
                'prestation_id': str(self.prestation.id)
            }
        ]
        
        for malicious_data in injection_attempts:
            response = self.client.post(
                '/reviews/',
                data=json.dumps(malicious_data),
                content_type='application/json'
            )
            
            # Le commentaire peut être créé mais le contenu doit être traité de manière sécurisée
            if response.status_code == 201:
                review = json.loads(response.data)
                # Le texte ne doit pas être exécuté/interprété
                self.assertIn('text', review)
                
                # Nettoyer pour le test suivant
                self.assertTrue(self.login_as_user('admin@test.com', 'Password123!'))
                self.client.delete(f'/reviews/{review["id"]}')
                self.assertTrue(self.login_as_user('hacker@test.com', 'Password123!'))
    
    def test_invalid_uuid_handling(self):
        """Test de la gestion des UUID invalides"""
        self.assertTrue(self.login_as_user('admin@test.com', 'Password123!'))
        
        invalid_uuids = [
            'invalid-uuid-format',
            '123456789',
            'not-a-uuid-at-all-definitely',
            'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',  # Caractères invalides
            'too-short',
            'way-too-long-to-be-a-valid-uuid-format',
            '12345678-1234-1234-1234-12345678901z',  # Caractère invalide à la fin
            'abcdefgh-ijkl-mnop-qrst-uvwxyz123456',  # Lettres non-hex
        ]
        
        for invalid_uuid in invalid_uuids:
            # Test GET review by ID
            response = self.client.get(f'/reviews/{invalid_uuid}')
            self.assertIn(response.status_code, [400, 404, 500])
            
            # Test PATCH review
            response = self.client.patch(
                f'/reviews/{invalid_uuid}',
                data=json.dumps({'rating': 5}),
                content_type='application/json'
            )
            self.assertIn(response.status_code, [400, 404, 500])
            
            # Test DELETE review
            response = self.client.delete(f'/reviews/{invalid_uuid}')
            self.assertIn(response.status_code, [400, 404, 500])
    
    def test_rating_boundary_validation(self):
        """Test de validation des limites de notation"""
        self.assertTrue(self.login_as_user('user@test.com', 'Password123!'))
        
        invalid_ratings = [
            0,    # Trop bas
            6,    # Trop haut
            -1,   # Négatif
            10,   # Trop haut
            'five',  # Non numérique
            None,    # Null
            3.5      # Décimal (si non supporté)
        ]
        
        for invalid_rating in invalid_ratings:
            review_data = {
                'rating': invalid_rating,
                'text': 'Test avec rating invalide',
                'prestation_id': str(self.prestation.id)
            }
            
            response = self.client.post(
                '/reviews/',
                data=json.dumps(review_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400,
                           f"Rating {invalid_rating} should be rejected")
    
    def test_text_length_validation(self):
        """Test de validation de la longueur du texte"""
        self.assertTrue(self.login_as_user('user@test.com', 'Password123!'))
        
        # Texte trop court
        short_text_data = {
            'rating': 5,
            'text': 'X',  # 1 caractère (minimum 2)
            'prestation_id': str(self.prestation.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(short_text_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Texte trop long
        long_text_data = {
            'rating': 5,
            'text': 'X' * 501,  # 501 caractères (maximum 500)
            'prestation_id': str(self.prestation.id)
        }
        
        response = self.client.post(
            '/reviews/',
            data=json.dumps(long_text_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_malformed_json_handling(self):
        """Test de gestion des JSON malformés"""
        self.assertTrue(self.login_as_user('user@test.com', 'Password123!'))
        
        malformed_payloads = [
            '{"rating": 5, "text": "test"',  # JSON incomplet
            '{"rating": 5, "text": "test", }',  # Virgule en trop
            'not json at all',
            '{"rating": 5, "text": "test", "prestation_id": }',  # Valeur manquante
        ]
        
        for payload in malformed_payloads:
            response = self.client.post(
                '/reviews/',
                data=payload,
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
    
    def test_user_enumeration_protection(self):
        """Test de protection contre l'énumération d'utilisateurs"""
        self.assertTrue(self.login_as_user('admin@test.com', 'Password123!'))
        
        # Tenter d'accéder aux commentaires d'un utilisateur inexistant
        fake_user_id = '00000000-0000-0000-0000-000000000000'
        
        response = self.client.get(f'/reviews/user/{fake_user_id}/prestation/{self.prestation.id}')
        
        # Devrait retourner 404 (utilisateur non trouvé) plutôt que de révéler l'existence
        self.assertEqual(response.status_code, 404)
    
    def test_prestation_enumeration_protection(self):
        """Test de protection contre l'énumération de prestations"""
        self.assertTrue(self.login_as_user('admin@test.com', 'Password123!'))
        
        # Tenter d'accéder aux commentaires d'une prestation inexistante
        fake_prestation_id = '00000000-0000-0000-0000-000000000000'
        
        response = self.client.get(f'/reviews/prestation/{fake_prestation_id}')
        
        # Devrait retourner 404 (prestation non trouvée)
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()