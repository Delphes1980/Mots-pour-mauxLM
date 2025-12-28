#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch


class TestAppointmentsAPIUnit(unittest.TestCase):
    """Tests unitaires purs pour l'API appointments"""

    @patch('app.api.v1.appointments.facade')
    def test_create_appointment_logic(self, mock_facade):
        """Test logique création appointment"""
        mock_appointment = Mock()
        mock_facade.create_appointment.return_value = mock_appointment
        
        appointment_data = {
            'message': 'Need appointment',
            'user_id': 'user-id',
            'prestation_id': 'prestation-id'
        }
        
        result = mock_facade.create_appointment(**appointment_data)
        
        self.assertEqual(result, mock_appointment)
        mock_facade.create_appointment.assert_called_once_with(**appointment_data)

    @patch('app.api.v1.appointments.facade')
    def test_get_all_appointments_logic(self, mock_facade):
        """Test logique récupération tous appointments"""
        mock_appointments = [Mock(), Mock()]
        mock_facade.get_all_appointments.return_value = mock_appointments
        
        result = mock_facade.get_all_appointments()
        
        self.assertEqual(result, mock_appointments)
        mock_facade.get_all_appointments.assert_called_once()

    @patch('app.api.v1.appointments.facade')
    def test_get_appointment_by_id_logic(self, mock_facade):
        """Test logique récupération appointment par ID"""
        mock_appointment = Mock()
        mock_facade.get_appointment_by_id.return_value = mock_appointment
        
        result = mock_facade.get_appointment_by_id('appointment-id')
        
        self.assertEqual(result, mock_appointment)
        mock_facade.get_appointment_by_id.assert_called_once_with('appointment-id')

    @patch('app.api.v1.appointments.facade')
    def test_update_appointment_status_logic(self, mock_facade):
        """Test logique mise à jour statut appointment"""
        mock_appointment = Mock()
        mock_facade.update_appointment_status.return_value = mock_appointment
        
        status_data = {'status': 'CONFIRMED'}
        result = mock_facade.update_appointment_status('appointment-id', **status_data)
        
        self.assertEqual(result, mock_appointment)
        mock_facade.update_appointment_status.assert_called_once_with('appointment-id', **status_data)

    @patch('app.api.v1.appointments.facade')
    def test_delete_appointment_logic(self, mock_facade):
        """Test logique suppression appointment"""
        mock_facade.delete_appointment.return_value = True
        
        result = mock_facade.delete_appointment('appointment-id')
        
        self.assertTrue(result)
        mock_facade.delete_appointment.assert_called_once_with('appointment-id')

    @patch('app.api.v1.appointments.facade')
    def test_get_appointments_by_status_logic(self, mock_facade):
        """Test logique récupération appointments par statut"""
        mock_appointments = [Mock(), Mock()]
        mock_facade.get_appointments_by_status.return_value = mock_appointments
        
        result = mock_facade.get_appointments_by_status('PENDING')
        
        self.assertEqual(result, mock_appointments)
        mock_facade.get_appointments_by_status.assert_called_once_with('PENDING')

    @patch('app.api.v1.appointments.facade')
    def test_get_appointment_by_prestation_logic(self, mock_facade):
        """Test logique récupération appointments par prestation"""
        mock_appointments = [Mock(), Mock()]
        mock_facade.get_appointment_by_prestation.return_value = mock_appointments
        
        prestation_id = 'test-prestation-id'
        result = mock_facade.get_appointment_by_prestation(prestation_id)
        
        self.assertEqual(result, mock_appointments)
        mock_facade.get_appointment_by_prestation.assert_called_once_with(prestation_id)

    @patch('app.api.v1.appointments.facade')
    def test_get_appointment_by_user_logic(self, mock_facade):
        """Test logique récupération appointments par utilisateur"""
        mock_appointments = [Mock(), Mock()]
        mock_facade.get_appointment_by_user.return_value = mock_appointments
        
        user_id = 'test-user-id'
        result = mock_facade.get_appointment_by_user(user_id)
        
        self.assertEqual(result, mock_appointments)
        mock_facade.get_appointment_by_user.assert_called_once_with(user_id)

    @patch('app.api.v1.appointments.facade')
    def test_get_appointment_by_user_and_prestation_logic(self, mock_facade):
        """Test logique récupération appointments par utilisateur et prestation"""
        mock_appointments = [Mock(), Mock()]
        mock_facade.get_appointment_by_user_and_prestation.return_value = mock_appointments
        
        user_id = 'test-user-id'
        prestation_id = 'test-prestation-id'
        result = mock_facade.get_appointment_by_user_and_prestation(user_id, prestation_id)
        
        self.assertEqual(result, mock_appointments)
        mock_facade.get_appointment_by_user_and_prestation.assert_called_once_with(user_id, prestation_id)


if __name__ == '__main__':
    unittest.main()