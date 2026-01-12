#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch


class TestAppointmentRepositoryComprehensive(unittest.TestCase):
    """Tests unitaires complets pour AppointmentRepository"""

    @patch('app.db')
    @patch('app.persistence.AppointmentRepository.Appointment')
    @patch('app.persistence.AppointmentRepository.text_field_validation')
    @patch('app.persistence.AppointmentRepository.type_validation')
    @patch('app.persistence.AppointmentRepository.is_valid_uuid4')
    def test_create_appointment(self, mock_uuid_val, mock_type_val, mock_text_val, mock_appt_class, mock_db):
        """Test création appointment"""
        from app.persistence.AppointmentRepository import AppointmentRepository
        
        mock_text_val.return_value = 'Message'
        mock_type_val.return_value = None
        mock_uuid_val.return_value = True

        mock_appt_instance = Mock()
        mock_appt_class.return_value = mock_appt_instance

        mock_session = Mock()
        mock_db.session = mock_session
        
        mock_user = Mock()
        mock_user.id = 'user-id'
        mock_prestation = Mock()
        mock_prestation.id = 'prestation-id'
        
        repo = AppointmentRepository()
        result = repo.create_appointment('Message', mock_user, mock_prestation)
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        self.assertIsNotNone(result)

    @patch('app.db')
    def test_get_appointments_by_status(self, mock_db):
        """Test récupération appointments par statut"""
        from app.persistence.AppointmentRepository import AppointmentRepository
        
        mock_appointments = [Mock(), Mock()]
        mock_session = Mock()
        mock_query = Mock()
        mock_filter_by = Mock()
        mock_filter_by.all.return_value = mock_appointments
        mock_query.filter_by.return_value = mock_filter_by
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = AppointmentRepository()
        result = repo.get_appointments_by_status('PENDING')
        
        self.assertEqual(result, mock_appointments)

    @patch('app.db')
    def test_get_by_user_and_prestation(self, mock_db):
        """Test récupération appointments par user et prestation"""
        from app.persistence.AppointmentRepository import AppointmentRepository
        
        mock_appointments = [Mock(), Mock()]
        mock_session = Mock()
        mock_query = Mock()
        mock_filter_by = Mock()
        mock_filter_by.all.return_value = mock_appointments
        mock_query.filter_by.return_value = mock_filter_by
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = AppointmentRepository()
        result = repo.get_by_user_and_prestation('user_id', 'prestation_id')
        
        self.assertEqual(result, mock_appointments)

    @patch('app.db')
    def test_get_by_prestation_id(self, mock_db):
        """Test récupération appointments par prestation"""
        from app.persistence.AppointmentRepository import AppointmentRepository
        
        mock_appointments = [Mock(), Mock()]
        mock_session = Mock()
        mock_query = Mock()
        mock_filter_by = Mock()
        mock_filter_by.all.return_value = mock_appointments
        mock_query.filter_by.return_value = mock_filter_by
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = AppointmentRepository()
        result = repo.get_by_prestation_id('prestation_id')
        
        self.assertEqual(result, mock_appointments)

    @patch('app.db')
    def test_get_by_user_id(self, mock_db):
        """Test récupération appointments par utilisateur"""
        from app.persistence.AppointmentRepository import AppointmentRepository
        
        mock_appointments = [Mock(), Mock()]
        mock_session = Mock()
        mock_query = Mock()
        mock_filter_by = Mock()
        mock_filter_by.all.return_value = mock_appointments
        mock_query.filter_by.return_value = mock_filter_by
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = AppointmentRepository()
        result = repo.get_by_user_id('user_id')
        
        self.assertEqual(result, mock_appointments)

    @patch('app.db')
    @patch('app.utils.is_valid_uuid4')
    def test_reassign_appointments_from_user(self, mock_uuid_val, mock_db):
        """Test réassignation appointments utilisateur"""
        from app.persistence.AppointmentRepository import AppointmentRepository
        from uuid import uuid4
        
        mock_uuid_val.return_value = True
        mock_old_user = Mock()
        mock_new_user = Mock()
        mock_appointments = [Mock(), Mock()]
        mock_session = Mock()
        mock_session.query.return_value.get.side_effect = [mock_old_user, mock_new_user]
        mock_db.session = mock_session
        
        repo = AppointmentRepository()
        repo.get_by_user_id = Mock(return_value=mock_appointments)
        
        result = repo.reassign_appointments_from_user(str(uuid4()), str(uuid4()))
        
        self.assertEqual(result, 2)
        mock_session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()