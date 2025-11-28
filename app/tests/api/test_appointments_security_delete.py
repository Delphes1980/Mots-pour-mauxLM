#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.appointments import api as appointments_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment


class TestAppointmentsSecurityDelete(BaseTest):
    """Tests de sécurité pour la suppression de rendez-vous - API"""

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

    def test_delete_appointment_requires_authentication(self):
        """Test sécurité - authentification requise"""
        appointment = Appointment(user=self.regular_user, message="Auth test", prestation=self.prestation)
        self.save_to_db(appointment)
        
        unauthenticated_client = self.app.test_client()
        response = unauthenticated_client.delete(f'/appointments/{appointment.id}')
        
        self.assertEqual(response.status_code, 401)

    def test_delete_appointment_requires_admin_rights(self):
        """Test sécurité - droits admin requis"""
        appointment = Appointment(user=self.regular_user, message="Admin test", prestation=self.prestation)
        self.save_to_db(appointment)
        
        user_client = self.login_as_user()
        response = user_client.delete(f'/appointments/{appointment.id}')
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('administrateur', response_data['error'])

    def test_delete_appointment_sql_injection_protection(self):
        """Test sécurité - protection injection SQL"""
        self.login_as_admin()
        
        malicious_ids = [
            "'; DROP TABLE appointments; --",
            "1' OR '1'='1",
            "admin' UNION SELECT * FROM users --",
            "../../../etc/passwd",
            "<script>alert('xss')</script>"
        ]
        
        for malicious_id in malicious_ids:
            response = self.client.delete(f'/appointments/{malicious_id}')
            
            # Doit échouer avec validation (400) ou not found (404), pas avec erreur SQL
            self.assertIn(response.status_code, [400, 404])
            
            # Vérifier le JSON seulement si la réponse en contient
            if response.data and response.content_type == 'application/json':
                response_data = json.loads(response.data)
                self.assertIn('error', response_data)
                
                # Vérifier qu'il n'y a pas de fuite d'informations SQL
                error_msg = response_data['error'].lower()
                sql_terms = ['sql', 'database', 'table', 'query', 'select', 'drop']
                for term in sql_terms:
                    self.assertNotIn(term, error_msg)

    def test_delete_appointment_authorization_bypass_protection(self):
        """Test sécurité - protection contournement autorisation"""
        appointment = Appointment(user=self.regular_user, message="Bypass test", prestation=self.prestation)
        self.save_to_db(appointment)
        
        user_client = self.login_as_user()
        
        # Test tentative de suppression sans droits admin
        response = user_client.delete(f'/appointments/{appointment.id}')
        self.assertEqual(response.status_code, 403)
        
        # Test avec headers malveillants
        malicious_headers = {
            'X-Admin': 'true',
            'X-Override-Auth': 'admin',
            'Authorization': 'Bearer admin-token'
        }
        
        response = user_client.delete(f'/appointments/{appointment.id}', headers=malicious_headers)
        self.assertEqual(response.status_code, 403)

    def test_delete_appointment_rate_limiting_simulation(self):
        """Test sécurité - simulation limitation de taux"""
        self.login_as_admin()
        
        appointments = []
        for i in range(5):
            appointment = Appointment(user=self.regular_user, message=f"Rate test {i}", prestation=self.prestation)
            self.save_to_db(appointment)
            appointments.append(appointment)
        
        # Supprimer rapidement plusieurs rendez-vous
        for appointment in appointments:
            response = self.client.delete(f'/appointments/{appointment.id}')
            # Doit réussir (pas de limitation implémentée actuellement)
            self.assertIn(response.status_code, [200, 404])

    def test_delete_appointment_error_message_information_disclosure(self):
        """Test sécurité - pas de fuite d'informations dans les erreurs"""
        self.login_as_admin()
        
        response = self.client.delete('/appointments/12345678-1234-1234-1234-123456789012')
        
        self.assertEqual(response.status_code, 404)
        
        # Vérifier le JSON seulement si la réponse en contient
        if response.data and response.content_type == 'application/json':
            response_data = json.loads(response.data)
            
            # Le message d'erreur ne doit pas révéler d'informations sensibles
            error_msg = response_data.get('error', '').lower()
            sensitive_terms = ['sql', 'database', 'table', 'column', 'query', 'internal']
            
            for term in sensitive_terms:
                self.assertNotIn(term, error_msg)

    def test_delete_appointment_concurrent_access_protection(self):
        """Test sécurité - protection accès concurrent"""
        appointment = Appointment(user=self.regular_user, message="Concurrent test", prestation=self.prestation)
        self.save_to_db(appointment)
        
        self.login_as_admin()
        
        # Simuler deux suppressions simultanées
        response1 = self.client.delete(f'/appointments/{appointment.id}')
        response2 = self.client.delete(f'/appointments/{appointment.id}')
        
        # Une doit réussir, l'autre échouer
        responses = [response1.status_code, response2.status_code]
        self.assertIn(200, responses)
        self.assertIn(404, responses)

    def test_delete_appointment_input_validation_security(self):
        """Test sécurité - validation stricte des entrées"""
        self.login_as_admin()
        
        # Test avec différents types d'entrées malveillantes
        malicious_inputs = [
            'null',  # Chaîne null
            '0',  # Zéro
            '-1',  # Négatif
            'invalid-uuid',  # UUID invalide
            'a' * 1000,  # Très long
            '12345',  # Nombre simple
            'not-a-uuid-at-all'  # Clairement pas un UUID
        ]
        
        for malicious_input in malicious_inputs:
            response = self.client.delete(f'/appointments/{malicious_input}')
            # Peut être 400 (validation) ou 404 (not found) selon l'implémentation
            self.assertIn(response.status_code, [400, 404])
            
            # Vérifier le JSON seulement si la réponse en contient
            if response.data and response.content_type == 'application/json':
                response_data = json.loads(response.data)
                self.assertIn('error', response_data)


if __name__ == '__main__':
    unittest.main()