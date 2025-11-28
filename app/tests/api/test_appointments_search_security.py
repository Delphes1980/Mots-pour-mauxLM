#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.appointments import api as appointments_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment, AppointmentStatus


class TestAppointmentsSearchSecurity(BaseTest):
    """Tests de sécurité pour la recherche de rendez-vous par statut - API"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(appointments_api, path='/appointments')
        self.client = self.app.test_client()

        # Créer utilisateurs
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
        
        self.prestation = Prestation(name='Security Test Prestation')
        self.save_to_db(self.admin_user, self.regular_user, self.prestation)

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def login_as_user(self):
        user_client = self.app.test_client()
        credentials = {'email': 'user@test.com', 'password': 'Password123!'}
        response = user_client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        return user_client

    def test_search_appointments_requires_authentication(self):
        """Test sécurité - authentification requise"""
        unauthenticated_client = self.app.test_client()
        response = unauthenticated_client.get('/appointments/search?status=PENDING')
        
        self.assertEqual(response.status_code, 401)

    def test_search_appointments_requires_admin_rights(self):
        """Test sécurité - droits admin requis"""
        user_client = self.login_as_user()
        response = user_client.get('/appointments/search?status=PENDING')
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('administrateur', response_data['error'])

    def test_search_appointments_sql_injection_protection(self):
        """Test sécurité - protection injection SQL"""
        self.login_as_admin()
        
        malicious_statuses = [
            "'; DROP TABLE appointments; --",
            "PENDING' OR '1'='1",
            "admin' UNION SELECT * FROM users --",
            "../../../etc/passwd",
            "<script>alert('xss')</script>",
            "PENDING'; DELETE FROM appointments; --"
        ]
        
        for malicious_status in malicious_statuses:
            response = self.client.get(f'/appointments/search?status={malicious_status}')
            
            # Doit échouer avec validation (400), pas avec erreur SQL
            self.assertEqual(response.status_code, 400)
            
            # Vérifier le JSON seulement si la réponse en contient
            if response.data and response.content_type == 'application/json':
                response_data = json.loads(response.data)
                self.assertIn('error', response_data)
                
                # Vérifier qu'il n'y a pas de fuite d'informations SQL
                error_msg = response_data['error'].lower()
                sql_terms = ['sql', 'database', 'table', 'query', 'select', 'drop', 'delete']
                for term in sql_terms:
                    self.assertNotIn(term, error_msg)

    def test_search_appointments_authorization_bypass_protection(self):
        """Test sécurité - protection contournement autorisation"""
        user_client = self.login_as_user()
        
        # Test avec headers malveillants
        malicious_headers = {
            'X-Admin': 'true',
            'X-Override-Auth': 'admin',
            'Authorization': 'Bearer admin-token'
        }
        
        response = user_client.get('/appointments/search?status=PENDING', headers=malicious_headers)
        self.assertEqual(response.status_code, 403)

    def test_search_appointments_parameter_tampering_protection(self):
        """Test sécurité - protection manipulation de paramètres"""
        self.login_as_admin()
        
        # Test avec différents types de manipulation de paramètres
        malicious_params = [
            'status=PENDING&admin=true',
            'status=PENDING&user_id=1',
            'status=PENDING&bypass=1',
            'status=PENDING&debug=true',
            'status=PENDING&limit=999999'
        ]
        
        for params in malicious_params:
            response = self.client.get(f'/appointments/search?{params}')
            # Doit soit réussir normalement soit échouer proprement
            self.assertIn(response.status_code, [200, 400, 404])

    def test_search_appointments_rate_limiting_simulation(self):
        """Test sécurité - simulation limitation de taux"""
        self.login_as_admin()
        
        # Faire plusieurs requêtes rapidement
        for i in range(10):
            response = self.client.get('/appointments/search?status=PENDING')
            # Doit réussir (pas de limitation implémentée actuellement)
            self.assertIn(response.status_code, [200, 404])

    def test_search_appointments_error_message_information_disclosure(self):
        """Test sécurité - pas de fuite d'informations dans les erreurs"""
        self.login_as_admin()
        
        response = self.client.get('/appointments/search?status=INVALID_STATUS')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        
        # Le message d'erreur ne doit pas révéler d'informations sensibles
        error_msg = response_data.get('error', '').lower()
        sensitive_terms = ['sql', 'database', 'table', 'column', 'query', 'internal', 'stack', 'trace']
        
        for term in sensitive_terms:
            self.assertNotIn(term, error_msg)

    def test_search_appointments_input_validation_security(self):
        """Test sécurité - validation stricte des entrées"""
        self.login_as_admin()
        
        # Test avec différents types d'entrées malveillantes
        malicious_inputs = [
            'null',  # Chaîne null
            '0',  # Zéro
            '-1',  # Négatif
            'a' * 1000,  # Très long
            '12345',  # Nombre
            'PENDING\x00',  # Caractère null
            'PENDING\n\r',  # Caractères de contrôle
            '%50%45%4E%44%49%4E%47',  # URL encoded
        ]
        
        for malicious_input in malicious_inputs:
            response = self.client.get(f'/appointments/search?status={malicious_input}')
            # Doit échouer avec validation (400) ou réussir si input valide
            self.assertIn(response.status_code, [200, 400, 404])
            
            # Vérifier le JSON seulement si la réponse en contient
            if response.status_code == 400 and response.data and response.content_type == 'application/json':
                response_data = json.loads(response.data)
                self.assertIn('error', response_data)

    def test_search_appointments_concurrent_access_protection(self):
        """Test sécurité - protection accès concurrent"""
        appointment = Appointment(user=self.regular_user, message="Concurrent test", prestation=self.prestation)
        appointment.status = AppointmentStatus.PENDING
        self.save_to_db(appointment)
        
        self.login_as_admin()
        
        # Simuler deux recherches simultanées
        response1 = self.client.get('/appointments/search?status=PENDING')
        response2 = self.client.get('/appointments/search?status=PENDING')
        
        # Les deux doivent réussir
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

    def test_search_appointments_case_sensitivity_security(self):
        """Test sécurité - sensibilité à la casse"""
        self.login_as_admin()
        
        # Test avec différentes casses
        case_variations = [
            'pending',  # minuscule
            'Pending',  # première lettre majuscule
            'PENDING',  # majuscule (valide)
            'pEnDiNg',  # casse mixte
        ]
        
        for variation in case_variations:
            response = self.client.get(f'/appointments/search?status={variation}')
            # Seul PENDING devrait être accepté
            if variation == 'PENDING':
                self.assertIn(response.status_code, [200, 404])
            else:
                self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()