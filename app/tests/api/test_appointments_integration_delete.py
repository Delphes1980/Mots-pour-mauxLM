#!/usr/bin/env python3

import json
import unittest
from app.tests.base_test import BaseTest
from app.api.v1.authentication import api as auth_api
from app.api.v1.appointments import api as appointments_api
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment


class TestAppointmentsIntegrationDelete(BaseTest):
    """Tests d'intégration pour la suppression de rendez-vous - API avec vraie DB"""

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
        
        # Créer prestation
        self.prestation = Prestation(name='Integration Test Prestation')
        
        self.save_to_db(self.admin_user, self.regular_user, self.prestation)
        self.login_as_admin()

    def login_as_admin(self):
        """Se connecter en tant qu'admin"""
        credentials = {'email': 'admin@test.com', 'password': 'Password123!'}
        response = self.client.post('/auth/login', data=json.dumps(credentials), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_delete_appointment_full_integration(self):
        """Test d'intégration complet - création puis suppression"""
        # Créer un rendez-vous
        appointment = Appointment(
            user=self.regular_user,
            message="Integration delete test",
            prestation=self.prestation
        )
        self.save_to_db(appointment)
        
        # Vérifier qu'il existe
        get_response = self.client.get(f'/appointments/{appointment.id}')
        self.assertEqual(get_response.status_code, 200)
        
        # Supprimer
        delete_response = self.client.delete(f'/appointments/{appointment.id}')
        self.assertEqual(delete_response.status_code, 200)
        
        response_data = json.loads(delete_response.data)
        self.assertEqual(response_data['message'], 'Rendez-vous supprimé avec succès')
        
        # Vérifier qu'il n'existe plus
        get_response_after = self.client.get(f'/appointments/{appointment.id}')
        self.assertEqual(get_response_after.status_code, 404)

    def test_delete_appointment_impact_on_lists_integration(self):
        """Test d'intégration - impact sur les listes"""
        # Créer plusieurs rendez-vous
        appointment1 = Appointment(user=self.regular_user, message="Test 1", prestation=self.prestation)
        appointment2 = Appointment(user=self.regular_user, message="Test 2", prestation=self.prestation)
        self.save_to_db(appointment1, appointment2)
        
        # Vérifier qu'il y en a 2
        list_response = self.client.get('/appointments/')
        self.assertEqual(list_response.status_code, 200)
        appointments_list = json.loads(list_response.data)
        self.assertEqual(len(appointments_list), 2)
        
        # Supprimer un
        delete_response = self.client.delete(f'/appointments/{appointment1.id}')
        self.assertEqual(delete_response.status_code, 200)
        
        # Vérifier qu'il n'en reste qu'un
        list_response_after = self.client.get('/appointments/')
        appointments_list_after = json.loads(list_response_after.data)
        self.assertEqual(len(appointments_list_after), 1)
        self.assertEqual(appointments_list_after[0]['id'], str(appointment2.id))

    def test_delete_appointment_invalid_id_integration(self):
        """Test d'intégration - IDs invalides"""
        invalid_ids = ['invalid-id', '12345678-1234-1234-1234-123456789012']
        
        for invalid_id in invalid_ids:
            response = self.client.delete(f'/appointments/{invalid_id}')
            
            if invalid_id == '12345678-1234-1234-1234-123456789012':
                self.assertEqual(response.status_code, 404)
            else:
                self.assertEqual(response.status_code, 400)

    def test_delete_appointment_multiple_times_integration(self):
        """Test d'intégration - suppression multiple"""
        appointment = Appointment(user=self.regular_user, message="Multiple delete", prestation=self.prestation)
        self.save_to_db(appointment)
        
        # Première suppression
        response1 = self.client.delete(f'/appointments/{appointment.id}')
        self.assertEqual(response1.status_code, 200)
        
        # Deuxième suppression
        response2 = self.client.delete(f'/appointments/{appointment.id}')
        self.assertEqual(response2.status_code, 404)


if __name__ == '__main__':
    unittest.main()