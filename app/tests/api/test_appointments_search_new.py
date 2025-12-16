#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.appointments import api as appointments_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment, AppointmentStatus

class TestAppointmentsSearchAPI(BaseTest):
    """Tests API appointments search - Tests pour /appointments/search"""

    def setUp(self):
        super().setUp()
        self.api = self.create_test_api('Main')
        self.api.add_namespace(auth_api, path='/auth')
        self.api.add_namespace(appointments_api, path='/appointments')
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

        self.login_as_admin()

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def login_as_user(self):
        credentials = {'email': 'user@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_search_appointments_by_status_success(self):
        """Test recherche par statut réussie"""
        # Créer appointments avec différents statuts
        appointment1 = Appointment(
            user=self.regular_user,
            message='RDV pending',
            prestation=self.prestation
        )
        appointment1.status = AppointmentStatus.PENDING
        
        appointment2 = Appointment(
            user=self.regular_user,
            message='RDV confirmed',
            prestation=self.prestation
        )
        appointment2.status = AppointmentStatus.CONFIRMED
        
        self.save_to_db(appointment1, appointment2)

        response = self.client.get('/appointments/search?status=PENDING')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['status'], 'PENDING')

    def test_search_appointments_missing_status(self):
        """Test recherche sans paramètre status"""
        response = self.client.get('/appointments/search')
        self.assertEqual(response.status_code, 400)

    def test_search_appointments_invalid_status(self):
        """Test recherche avec statut invalide"""
        response = self.client.get('/appointments/search?status=INVALID')
        self.assertEqual(response.status_code, 400)

    def test_search_appointments_requires_admin(self):
        """Test que la recherche nécessite des droits admin"""
        self.login_as_user()
        response = self.client.get('/appointments/search?status=PENDING')
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()