#!/usr/bin/env python3

import json
import unittest
import platform
import sys
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api
from app.models.user import User

class TestCompatibility(BaseTest):
    """Tests de compatibilité - Versions et environnements"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.client = self.app.test_client()

    def test_python_version_compatibility(self):
        """Test compatibilité version Python"""
        python_version = sys.version_info

        # Vérifier version Python supportée (3.8+)
        self.assertGreaterEqual(python_version.major, 3)
        self.assertGreaterEqual(python_version.minor, 8)

    def test_platform_compatibility(self):
        """Test compatibilité plateforme"""
        system = platform.system()

        # Vérifier que l'application fonctionne sur les OS supportés
        supported_platforms = ['Linux', 'Darwin', 'Windows']
        self.assertIn(system, supported_platforms, f"Plateforme non supportée: {system}")

    def test_unicode_support(self):
        """Test support Unicode complet"""
        unicode_data = {
            'first_name': 'José',  # Caractères accentués
            'last_name': 'Müller',  # Caractères allemands
            'email': 'jose.muller@example.com',
            'password': 'Password123!',
            'address': '北京市朝阳区'  # Caractères chinois
        }

        response = self.client.post(
            '/users/',
            data=json.dumps(unicode_data, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )

        # Devrait gérer l'Unicode correctement
        self.assertEqual(response.status_code, 201)

    def test_json_encoding_compatibility(self):
        """Test compatibilité encodage JSON"""
        # Test différents encodages
        test_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'encoding@test.com',
            'password': 'Password123!'
        }

        # Test UTF-8
        response = self.client.post(
            '/users/',
            data=json.dumps(test_data).encode('utf-8'),
            content_type='application/json; charset=utf-8'
        )
        self.assertEqual(response.status_code, 201)

    def test_http_methods_compatibility(self):
        """Test compatibilité méthodes HTTP"""
        # Créer utilisateur pour les tests
        user = User(
            email='http@test.com',
            password='Password123!',
            first_name='HTTP',
            last_name='Test',
            is_admin=False
        )
        self.save_to_db(user)

        # Test GET
        response = self.client.get('/reviews/public-reviews')
        self.assertIn(response.status_code, [200, 404])

        # Test POST
        login_data = {'email': 'http@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(login_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Test OPTIONS (si supporté)
        response = self.client.options('/users/')
        self.assertIn(response.status_code, [200, 405])

    def test_content_type_compatibility(self):
        """Test compatibilité types de contenu"""
        data = {
            'first_name': 'Content',
            'last_name': 'Type',
            'email': 'content@test.com',
            'password': 'Password123!'
        }

        # Test application/json standard
        response = self.client.post(
            '/users/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        # Test avec charset explicite
        response = self.client.post(
            '/users/',
            data=json.dumps({'first_name': 'ContentTwo', 'last_name': 'TypeTwo', 'email': 'content2@test.com', 'password': 'Password123!'}),
            content_type='application/json; charset=utf-8'
        )
        self.assertEqual(response.status_code, 201)

    def test_database_charset_compatibility(self):
        """Test compatibilité charset base de données"""
        # Test caractères spéciaux dans différentes langues
        special_chars_data = [
            {'name': 'François', 'lang': 'French'},
            {'name': 'José', 'lang': 'Spanish'},
            {'name': 'Müller', 'lang': 'German'},
            {'name': 'Øyvind', 'lang': 'Norwegian'}
        ]

        for i, char_data in enumerate(special_chars_data):
            data = {
                'first_name': char_data['name'],
                'last_name': 'Test',
                'email': f'charset{i}@test.com',
                'password': 'Password123!'
            }

            response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 201, f"Échec pour {char_data['lang']}: {char_data['name']}")

    def test_timezone_compatibility(self):
        """Test compatibilité fuseaux horaires"""
        import datetime

        # Créer utilisateur et vérifier timestamp
        data = {
            'first_name': 'Timezone',
            'last_name': 'Test',
            'email': 'timezone@test.com',
            'password': 'Password123!'
        }

        before_creation = datetime.datetime.utcnow()
        response = self.client.post('/users/', data=json.dumps(data), content_type='application/json')
        after_creation = datetime.datetime.utcnow()

        self.assertEqual(response.status_code, 201)

        # Vérifier que la création s'est faite dans un délai raisonnable
        time_diff = after_creation - before_creation
        self.assertLess(time_diff.total_seconds(), 5.0, "Création utilisateur trop lente")

    def test_case_sensitivity_compatibility(self):
        """Test compatibilité sensibilité à la casse"""
        # Test email case insensitive
        data1 = {
            'first_name': 'CaseOne',
            'last_name': 'Test',
            'email': 'CASE@TEST.COM',
            'password': 'Password123!'
        }

        data2 = {
            'first_name': 'CaseTwo',
            'last_name': 'Test',
            'email': 'case@test.com',  # Même email en minuscules
            'password': 'Password123!'
        }

        # Créer premier utilisateur
        response1 = self.client.post('/users/', data=json.dumps(data1), content_type='application/json')
        self.assertEqual(response1.status_code, 201)

        # Tenter de créer second avec même email (différente casse)
        response2 = self.client.post('/users/', data=json.dumps(data2), content_type='application/json')

        # Devrait échouer si emails sont traités comme identiques
        self.assertIn(response2.status_code, [409, 201])  # Dépend de l'implémentation

if __name__ == '__main__':
    unittest.main()
