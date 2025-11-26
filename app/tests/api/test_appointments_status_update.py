#!/usr/bin/env python3

import unittest
import json
from app.tests.base_test import BaseTest
from app.api.v1.appointments import api as appointments_api
from app.api.v1.authentication import api as auth_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment, AppointmentStatus


class TestAppointmentsStatusUpdateAPI(BaseTest):
    """Tests end-to-end pour l'API de mise à jour du statut des rendez-vous"""
    
    def setUp(self):
        super().setUp()
        
        # Configuration de l'API via BaseTest
        self.api = self.create_test_api('Main')
        self.api.add_namespace(appointments_api, path='/appointments')
        self.api.add_namespace(auth_api, path='/auth')
        
        # Client de test
        self.client = self.app.test_client()
        
        # Créer un admin
        self.admin_user = User(
            first_name='Admin',
            last_name='Test',
            email='admin@test.com',
            password='Password123!',
            is_admin=True
        )
        
        # Créer un utilisateur normal
        self.regular_user = User(
            first_name='User',
            last_name='Test',
            email='user@test.com',
            password='Password123!',
            is_admin=False
        )
        
        # Créer une prestation
        self.prestation = Prestation(name='Test Prestation')
        
        self.save_to_db(self.admin_user, self.regular_user, self.prestation)
        
        # Créer un rendez-vous de test
        self.appointment = Appointment(
            user=self.regular_user,
            message="Test appointment message",
            prestation=self.prestation
        )
        self.save_to_db(self.appointment)
        
        # Se connecter en tant qu'admin
        self.login_as_admin()

    def login_as_admin(self):
        """Se connecter en tant qu'admin"""
        credentials = {
            'email': 'admin@test.com',
            'password': 'Password123!'
        }
        response = self.client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        if response.status_code != 200:
            error_data = response.get_json()
            if error_data and 'utf-8' in str(error_data.get('error', '')):
                self.api = self.create_test_api('Retry')
                self.api.add_namespace(appointments_api, path='/appointments')
                self.api.add_namespace(auth_api, path='/auth')
                self.client = self.app.test_client()
                response = self.client.post(
                    '/auth/login',
                    data=json.dumps(credentials),
                    content_type='application/json'
                )
        self.assertEqual(response.status_code, 200)

    def login_as_user(self):
        """Se connecter en tant qu'utilisateur normal"""
        user_client = self.app.test_client()
        credentials = {
            'email': 'user@test.com',
            'password': 'Password123!'
        }
        response = user_client.post(
            '/auth/login',
            data=json.dumps(credentials),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        return user_client

    def test_update_appointment_status_success(self):
        """Test mise à jour réussie du statut"""
        data = {
            'status': AppointmentStatus.CONFIRMED
        }
        
        response = self.client.put(
            f'/appointments/{self.appointment.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data['status'], AppointmentStatus.CONFIRMED)
        self.assertEqual(response_data['id'], str(self.appointment.id))

    def test_update_appointment_status_all_valid_statuses(self):
        """Test mise à jour avec tous les statuts valides"""
        valid_statuses = [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.COMPLETED,
            AppointmentStatus.PENDING
        ]
        
        for status in valid_statuses:
            data = {'status': status}
            
            response = self.client.put(
                f'/appointments/{self.appointment.id}',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], status)

    def test_update_appointment_status_requires_admin(self):
        """Test que la mise à jour nécessite des droits admin"""
        user_client = self.login_as_user()
        
        data = {
            'status': AppointmentStatus.CONFIRMED
        }
        
        response = user_client.put(
            f'/appointments/{self.appointment.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    def test_update_appointment_status_requires_authentication(self):
        """Test que la mise à jour nécessite une authentification"""
        unauthenticated_client = self.app.test_client()
        
        data = {
            'status': AppointmentStatus.CONFIRMED
        }
        
        response = unauthenticated_client.put(
            f'/appointments/{self.appointment.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)

    def test_update_appointment_status_invalid_appointment_id(self):
        """Test avec ID de rendez-vous invalide"""
        data = {
            'status': AppointmentStatus.CONFIRMED
        }
        
        invalid_ids = [
            'invalid-id',
            '12345678-1234-1234-1234-123456789012'  # UUID valide mais inexistant
        ]
        
        for invalid_id in invalid_ids:
            response = self.client.put(
                f'/appointments/{invalid_id}',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            if invalid_id == '12345678-1234-1234-1234-123456789012':
                self.assertEqual(response.status_code, 404)
            else:
                self.assertEqual(response.status_code, 400)

    def test_update_appointment_status_invalid_status(self):
        """Test avec statut invalide"""
        invalid_statuses = [
            'invalid_status',
            'confirmed',  # Minuscule
            '',
            123,
            None
        ]
        
        for invalid_status in invalid_statuses:
            data = {'status': invalid_status}
            
            response = self.client.put(
                f'/appointments/{self.appointment.id}',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)

    def test_update_appointment_status_missing_status(self):
        """Test sans fournir de statut"""
        data = {}
        
        response = self.client.put(
            f'/appointments/{self.appointment.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('errors', response_data)

    def test_update_appointment_status_response_format(self):
        """Test le format de la réponse"""
        data = {
            'status': AppointmentStatus.COMPLETED
        }
        
        response = self.client.put(
            f'/appointments/{self.appointment.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Vérifier les champs requis
        required_fields = ['id', 'message', 'status', 'prestation_id', 'user_id']
        for field in required_fields:
            self.assertIn(field, response_data)
        
        self.assertEqual(response_data['status'], AppointmentStatus.COMPLETED)

    def test_update_appointment_status_persistence(self):
        """Test que la mise à jour est persistée"""
        data = {
            'status': AppointmentStatus.CANCELLED
        }
        
        response = self.client.put(
            f'/appointments/{self.appointment.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier via GET
        get_response = self.client.get(f'/appointments/{self.appointment.id}')
        self.assertEqual(get_response.status_code, 200)
        
        get_data = json.loads(get_response.data)
        self.assertEqual(get_data['status'], AppointmentStatus.CANCELLED)

    def test_update_appointment_status_multiple_updates(self):
        """Test mises à jour multiples"""
        statuses_sequence = [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.PENDING,
            AppointmentStatus.COMPLETED
        ]
        
        for status in statuses_sequence:
            data = {'status': status}
            
            response = self.client.put(
                f'/appointments/{self.appointment.id}',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertEqual(response_data['status'], status)



if __name__ == '__main__':
    unittest.main()