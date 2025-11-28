#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.appointments import api as appointments_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment


class TestAppointmentsDelete(BaseTest):
    """Tests pour la suppression de rendez-vous - API"""

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

    def test_delete_appointment_success(self):
        """Test suppression réussie d'un rendez-vous"""
        appointment = Appointment(user=self.regular_user, message="Test delete", prestation=self.prestation)
        self.save_to_db(appointment)
        
        self.login_as_admin()
        response = self.client.delete(f'/appointments/{appointment.id}')
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le rendez-vous a été supprimé
        # Forcer une nouvelle requête après expire_all()
        from app import db
        db.session.close()
        deleted_appointment = Appointment.query.get(appointment.id)
        self.assertIsNone(deleted_appointment)

    def test_delete_appointment_not_found(self):
        """Test suppression d'un rendez-vous inexistant"""
        self.login_as_admin()
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.delete(f'/appointments/{fake_id}')
        
        self.assertEqual(response.status_code, 404)

    def test_delete_appointment_requires_authentication(self):
        """Test suppression sans authentification"""
        appointment = Appointment(user=self.regular_user, message="Auth test", prestation=self.prestation)
        self.save_to_db(appointment)
        
        unauthenticated_client = self.app.test_client()
        response = unauthenticated_client.delete(f'/appointments/{appointment.id}')
        
        self.assertEqual(response.status_code, 401)

    def test_delete_appointment_requires_admin_rights(self):
        """Test suppression sans droits admin"""
        appointment = Appointment(user=self.regular_user, message="Admin test", prestation=self.prestation)
        self.save_to_db(appointment)
        
        self.login_as_user()
        response = self.client.delete(f'/appointments/{appointment.id}')
        
        self.assertEqual(response.status_code, 403)

    def test_delete_appointment_invalid_id_format(self):
        """Test suppression avec ID invalide"""
        self.login_as_admin()
        
        invalid_ids = ['invalid-id', '12345', 'not-a-uuid']
        for invalid_id in invalid_ids:
            response = self.client.delete(f'/appointments/{invalid_id}')
            self.assertIn(response.status_code, [400, 404])


if __name__ == '__main__':
    unittest.main()