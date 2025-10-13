import json
import unittest

from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.appointments import api as appointments_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment

class TestAppointmentsSecurity(BaseTest):
    """Tests de sécurité API appointments"""

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
        self.prestation1 = Prestation(name='Massage')
        self.save_to_db(self.prestation1)

    def login_as_regular_user(self):
        credentials = {'email': 'user@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_regular_user_cannot_list_appointments(self):
        """Un utilisateur normal ne peut pas lister tous les rendez-vous"""
        self.login_as_regular_user()
        response = self.client.get('/appointments/')
        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_list_appointments_by_user(self):
        """Un utilisateur normal ne peut pas lister les rendez-vous d'un autre utilisateur"""
        self.login_as_regular_user()
        response = self.client.get(f'/appointments/user/{self.admin_user.id}')
        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_list_appointments_by_prestation(self):
        """Un utilisateur normal ne peut pas lister les rendez-vous d'une prestation"""
        self.login_as_regular_user()
        response = self.client.get(f'/appointments/prestation/{self.prestation1.id}')
        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_get_appointment_by_id(self):
        """Un utilisateur normal ne peut pas accéder à un rendez-vous par ID"""
        self.login_as_regular_user()
        # Créer un rendez-vous
        appointment = Appointment(
            message='Test',
            user=self.regular_user,
            prestation=self.prestation1
        )
        self.save_to_db(appointment)
        response = self.client.get(f'/appointments/{appointment.id}')
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_create_appointment(self):
        """Un utilisateur non connecté ne peut pas créer de rendez-vous"""
        data = {
            'message': 'Test',
            'prestation_id': str(self.prestation1.id)
        }
        response = self.client.post(
            '/appointments/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
