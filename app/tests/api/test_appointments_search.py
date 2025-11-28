#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.appointments import api as appointments_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment, AppointmentStatus


class TestAppointmentsSearch(BaseTest):
    """Tests pour la recherche de rendez-vous par statut - API"""

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
        
        self.prestation = Prestation(name='Test Prestation')
        self.save_to_db(self.admin_user, self.regular_user, self.prestation)

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def login_as_user(self):
        credentials = {'email': 'user@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_search_appointments_by_status_success(self):
        """Test recherche réussie par statut"""
        # Créer des rendez-vous avec différents statuts
        appointment1 = Appointment(user=self.regular_user, message="RDV pending", prestation=self.prestation)
        appointment1.status = AppointmentStatus.PENDING
        
        appointment2 = Appointment(user=self.regular_user, message="RDV confirmed", prestation=self.prestation)
        appointment2.status = AppointmentStatus.CONFIRMED
        
        appointment3 = Appointment(user=self.regular_user, message="RDV pending 2", prestation=self.prestation)
        appointment3.status = AppointmentStatus.PENDING
        
        self.save_to_db(appointment1, appointment2, appointment3)
        
        self.login_as_admin()
        response = self.client.get('/appointments/search?status=PENDING')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        
        for appointment in response_data:
            self.assertEqual(appointment['status'], AppointmentStatus.PENDING)

    def test_search_appointments_by_status_confirmed(self):
        """Test recherche par statut CONFIRMED"""
        appointment = Appointment(user=self.regular_user, message="RDV confirmed", prestation=self.prestation)
        appointment.status = AppointmentStatus.CONFIRMED
        self.save_to_db(appointment)
        
        self.login_as_admin()
        response = self.client.get('/appointments/search?status=CONFIRMED')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['status'], AppointmentStatus.CONFIRMED)

    def test_search_appointments_by_status_cancelled(self):
        """Test recherche par statut CANCELLED"""
        appointment = Appointment(user=self.regular_user, message="RDV cancelled", prestation=self.prestation)
        appointment.status = AppointmentStatus.CANCELLED
        self.save_to_db(appointment)
        
        self.login_as_admin()
        response = self.client.get('/appointments/search?status=CANCELLED')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['status'], AppointmentStatus.CANCELLED)

    def test_search_appointments_by_status_completed(self):
        """Test recherche par statut COMPLETED"""
        appointment = Appointment(user=self.regular_user, message="RDV completed", prestation=self.prestation)
        appointment.status = AppointmentStatus.COMPLETED
        self.save_to_db(appointment)
        
        self.login_as_admin()
        response = self.client.get('/appointments/search?status=COMPLETED')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]['status'], AppointmentStatus.COMPLETED)

    def test_search_appointments_no_status_parameter(self):
        """Test recherche sans paramètre status"""
        self.login_as_admin()
        response = self.client.get('/appointments/search')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('requis', response_data['error'])

    def test_search_appointments_invalid_status(self):
        """Test recherche avec statut invalide"""
        self.login_as_admin()
        response = self.client.get('/appointments/search?status=INVALID_STATUS')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    def test_search_appointments_requires_authentication(self):
        """Test recherche sans authentification"""
        unauthenticated_client = self.app.test_client()
        response = unauthenticated_client.get('/appointments/search?status=PENDING')
        
        self.assertEqual(response.status_code, 401)

    def test_search_appointments_requires_admin_rights(self):
        """Test recherche sans droits admin"""
        self.login_as_user()
        response = self.client.get('/appointments/search?status=PENDING')
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('administrateur', response_data['error'])

    def test_search_appointments_no_results(self):
        """Test recherche sans résultats"""
        # Créer un rendez-vous avec un statut différent
        appointment = Appointment(user=self.regular_user, message="RDV pending", prestation=self.prestation)
        appointment.status = AppointmentStatus.PENDING
        self.save_to_db(appointment)
        
        self.login_as_admin()
        response = self.client.get('/appointments/search?status=COMPLETED')
        
        # Selon l'implémentation, peut retourner 404 ou 200 avec liste vide
        self.assertIn(response.status_code, [200, 404])


if __name__ == '__main__':
    unittest.main()