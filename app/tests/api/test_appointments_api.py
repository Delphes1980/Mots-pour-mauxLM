import json
import unittest
from flask_jwt_extended import create_access_token

from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.appointments import api as appointments_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment

class TestAppointmentsAPI(BaseTest):
    """Tests API appointments - End-to-end avec vraie DB"""

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
        self.other_user = User(
            email='other@test.com',
            password='Password123!',
            first_name='Other',
            last_name='User',
            is_admin=False
        )
        self.save_to_db(self.admin_user, self.regular_user, self.other_user)

        # Créer prestations
        self.prestation1 = Prestation(name='Massage')
        self.prestation2 = Prestation(name='Acupuncture')
        self.save_to_db(self.prestation1, self.prestation2)

        self.login_as_regular_user()

    def login_as_regular_user(self):
        credentials = {'email': 'user@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def login_as_admin(self):
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def login_as_other_user(self):
        credentials = {'email': 'other@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_create_appointment_success(self):
        """Test création réussie d'un rendez-vous"""
        data = {
            'message': 'Je souhaite un rendez-vous pour un massage.',
            'prestation_id': str(self.prestation1.id)
        }
        response = self.client.post(
            '/appointments/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], data['message'])
        self.assertEqual(response_data['prestation_id'], str(self.prestation1.id))
        self.assertIn('id', response_data)

        # Vérifier en DB
        appointment = Appointment.query.filter_by(user_id=self.regular_user.id).first()
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.message, data['message'])

    def test_create_appointment_invalid_prestation(self):
        """Test création avec prestation inexistante"""
        data = {
            'message': 'Test',
            'prestation_id': '00000000-0000-0000-0000-000000000000'
        }
        response = self.client.post(
            '/appointments/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_create_appointment_invalid_data(self):
        """Test création avec données invalides"""
        invalid_data_sets = [
            {},  # Pas de données
            {'message': 'Test'},  # Manque prestation_id
            {'prestation_id': str(self.prestation1.id)},  # Manque message
            {'message': '', 'prestation_id': str(self.prestation1.id)},  # Message vide
            {'message': 'X' * 501, 'prestation_id': str(self.prestation1.id)},  # Message trop long
        ]
        for data in invalid_data_sets:
            response = self.client.post(
                '/appointments/',
                data=json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 400)

    def test_create_appointment_without_login(self):
        """Test création sans être connecté"""
        self.client.post('/auth/logout')
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

    def test_get_all_appointments_as_admin(self):
        """Test récupération de tous les rendez-vous en tant qu'admin"""
        self.login_as_admin()
        # Créer des rendez-vous
        appointment1 = Appointment(
            message='RDV 1',
            user=self.regular_user,
            prestation=self.prestation1
        )
        appointment2 = Appointment(
            message='RDV 2',
            user=self.other_user,
            prestation=self.prestation2
        )
        self.save_to_db(appointment1, appointment2)
        response = self.client.get('/appointments/')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)

    def test_get_all_appointments_as_regular_user(self):
        """Test récupération de tous les rendez-vous en tant qu'utilisateur normal"""
        self.login_as_regular_user()
        response = self.client.get('/appointments/')
        self.assertEqual(response.status_code, 403)

    def test_get_appointments_by_prestation_as_admin(self):
        """Test récupération des rendez-vous par prestation en tant qu'admin"""
        self.login_as_admin()
        appointment1 = Appointment(
            message='RDV Massage',
            user=self.regular_user,
            prestation=self.prestation1
        )
        appointment2 = Appointment(
            message='RDV Massage 2',
            user=self.other_user,
            prestation=self.prestation1
        )
        appointment3 = Appointment(
            message='RDV Acupuncture',
            user=self.regular_user,
            prestation=self.prestation2
        )
        self.save_to_db(appointment1, appointment2, appointment3)
        response = self.client.get(f'/appointments/prestation/{self.prestation1.id}')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        for appt in response_data:
            self.assertEqual(appt['prestation_id'], str(self.prestation1.id))

    def test_get_appointments_by_user_as_admin(self):
        """Test récupération des rendez-vous par utilisateur en tant qu'admin"""
        self.login_as_admin()
        appointment1 = Appointment(
            message='RDV 1',
            user=self.regular_user,
            prestation=self.prestation1
        )
        appointment2 = Appointment(
            message='RDV 2',
            user=self.regular_user,
            prestation=self.prestation2
        )
        appointment3 = Appointment(
            message='RDV 3',
            user=self.other_user,
            prestation=self.prestation1
        )
        self.save_to_db(appointment1, appointment2, appointment3)
        response = self.client.get(f'/appointments/user/{self.regular_user.id}')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(len(response_data), 2)
        for appt in response_data:
            self.assertEqual(appt['user_id'], str(self.regular_user.id))

    def test_get_appointments_by_user_and_prestation_as_admin(self):
        """Test récupération des rendez-vous par utilisateur et prestation"""
        self.login_as_admin()
        appointment = Appointment(
            message='RDV spécifique',
            user=self.regular_user,
            prestation=self.prestation1
        )
        other_appointment = Appointment(
            message='Autre RDV',
            user=self.other_user,
            prestation=self.prestation1
        )
        self.save_to_db(appointment, other_appointment)
        response = self.client.get(f'/appointments/user/{self.regular_user.id}/prestation/{self.prestation1.id}')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        if isinstance(response_data, list):
            self.assertEqual(len(response_data), 1)
            self.assertEqual(response_data[0]['message'], 'RDV spécifique')
        else:
            self.assertEqual(response_data['message'], 'RDV spécifique')

    def test_get_appointment_by_id_as_admin(self):
        """Test récupération d'un rendez-vous par ID en tant qu'admin"""
        self.login_as_admin()
        appointment = Appointment(
            message='RDV test',
            user=self.regular_user,
            prestation=self.prestation1
        )
        self.save_to_db(appointment)
        response = self.client.get(f'/appointments/{appointment.id}')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'RDV test')
        self.assertEqual(response_data['id'], str(appointment.id))

    def test_get_appointment_by_id_not_found(self):
        """Test récupération d'un rendez-vous inexistant"""
        self.login_as_admin()
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(f'/appointments/{fake_id}')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
