#!/usr/bin/env python3
import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api


class TestAdvancedValidation(BaseTest):
    """Tests de validation avancée - Limites système et edge cases"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.client = self.app.test_client()

    def test_email_length_limits(self):
        """Test limites de longueur pour email"""
        # Email très long (> 254 caractères)
        long_email = 'a' * 240 + '@example.com'
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': long_email,
            'password': 'Password123!'
        }

        response = self.client.post(
            '/users/',
            data=json.dumps(data),
            content_type='application/json'
        )
        # Devrait échouer avec email trop long
        self.assertEqual(response.status_code, 400)

    def test_name_length_limits(self):
        """Test limites de longueur pour noms"""
        # Nom très long
        long_name = 'A' * 101  # > 100 caractères
        data = {
            'first_name': long_name,
            'last_name': 'Test',
            'email': 'test@example.com',
            'password': 'Password123!'
        }

        response = self.client.post(
            '/users/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_password_complexity_edge_cases(self):
        """Test cas limites de complexité mot de passe"""
        weak_passwords = [
            'password',  # Pas de majuscule, chiffre, caractère spécial
            'PASSWORD123',  # Pas de caractère spécial
            'Password!',  # Trop court (< 12 caractères)
            '12345678!',  # Pas de lettre
            'Aa1!',  # Trop court
            'A' * 129 + '1!',  # Trop long (> 128 caractères)
        ]

        for password in weak_passwords:
            data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': f'test{len(password)}@example.com',
                'password': password
            }

            response = self.client.post(
                '/users/',
                data=json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

    def test_unicode_characters_handling(self):
        """Test gestion des caractères Unicode"""
        unicode_data = {
            'first_name': 'José',  # Caractères accentués
            'last_name': 'Müller',  # Caractères allemands
            'email': 'jose.muller@example.com',
            'password': 'Password123!',
            'address': '123 Rue de la Paix, 75001 Paris 🇫🇷'  # Emoji
        }

        response = self.client.post(
            '/users/',
            data=json.dumps(unicode_data, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        # Devrait réussir avec caractères Unicode
        self.assertEqual(response.status_code, 201)

    def test_phone_number_formats(self):
        """Test formats de numéros de téléphone"""
        valid_phones = [
            '0123456789',
            '01 23 45 67 89',
            '01.23.45.67.89',
            '01-23-45-67-89',
            '+33123456789',
            '+33 1 23 45 67 89'
        ]

        for i, phone in enumerate(valid_phones):
            data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': f'test{i}@example.com',
                'password': 'Password123!',
                'phone_number': phone
            }

            response = self.client.post(
                '/users/',
                data=json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201, f"Phone {phone} should be valid")

    def test_invalid_phone_formats(self):
        """Test formats de téléphone invalides"""
        invalid_phones = [
            '123',  # Trop court
            'abcdefghij',  # Lettres
            '01234567890123456789',  # Trop long
            '+++33123456789',  # Trop de +
            ''  # Vide (mais fourni)
        ]

        for i, phone in enumerate(invalid_phones):
            data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': f'invalid{i}@example.com',
                'password': 'Password123!',
                'phone_number': phone
            }

            response = self.client.post(
                '/users/',
                data=json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400, f"Phone {phone} should be invalid")

    def test_email_format_edge_cases(self):
        """Test cas limites de format email"""
        invalid_emails = [
            'plainaddress',  # Pas de @
            '@missingdomain.com',  # Pas de partie locale
            'missing@.com',  # Pas de domaine
            'spaces @example.com',  # Espaces
            'double@@example.com',  # Double @
            'trailing.dot.@example.com',  # Point final avant @
            'example@',  # Pas de domaine après @
            'example@.com',  # Point au début du domaine
            'example@com.',  # Point à la fin
            'example@-domain.com',  # Tiret au début du domaine
            'example@domain-.com'  # Tiret à la fin du domaine
        ]

        for i, email in enumerate(invalid_emails):
            data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': email,
                'password': 'Password123!'
            }

            response = self.client.post(
                '/users/',
                data=json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400, f"Email {email} should be invalid")

    def test_json_payload_size_limits(self):
        """Test limites de taille des données JSON"""
        # Créer un payload très large
        large_address = 'A' * 10000  # 10KB d'adresse
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'Password123!',
            'address': large_address
        }

        response = self.client.post(
            '/users/',
            data=json.dumps(data),
            content_type='application/json'
        )
        # Devrait échouer avec données trop volumineuses
        self.assertIn(response.status_code, [400, 413])

    def test_null_byte_injection(self):
        """Test injection de caractères null"""
        null_byte_data = {
            'first_name': 'Test\x00Injection',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'Password123!'
        }

        response = self.client.post(
            '/users/',
            data=json.dumps(null_byte_data),
            content_type='application/json'
        )
        # Devrait échouer avec caractères null
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
