#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
from app.utils import CustomError


class TestPrestationServiceUnit(unittest.TestCase):
    """Tests unitaires purs pour PrestationService"""

    @patch('app.services.PrestationService.PrestationRepository')
    @patch('app.utils.text_field_validation')
    def test_create_prestation_success(self, mock_text_val, mock_repo_class):
        """Test création prestation réussie"""
        from app.services.PrestationService import PrestationService
        
        mock_text_val.return_value = 'Massage'
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_attribute.return_value = None
        mock_prestation = Mock()
        mock_repo.create_prestation.return_value = mock_prestation
        
        service = PrestationService()
        result = service.create_prestation(name='Massage')
        
        self.assertEqual(result, mock_prestation)
        mock_repo.create_prestation.assert_called_once_with(name='Massage')

    @patch('app.services.PrestationService.PrestationRepository')
    @patch('app.utils.text_field_validation')
    def test_create_prestation_already_exists(self, mock_text_val, mock_repo_class):
        """Test création prestation déjà existante"""
        from app.services.PrestationService import PrestationService
        
        mock_text_val.return_value = 'Massage'
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_attribute.return_value = Mock()  # Prestation existe
        
        service = PrestationService()
        
        with self.assertRaises(CustomError) as context:
            service.create_prestation(name='Massage')
        
        self.assertIn('existe déjà', str(context.exception))

    @patch('app.services.PrestationService.PrestationRepository')
    def test_get_all_prestations(self, mock_repo_class):
        """Test récupération toutes prestations"""
        from app.services.PrestationService import PrestationService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_prestations = [Mock(), Mock()]
        mock_repo.get_all.return_value = mock_prestations
        
        service = PrestationService()
        result = service.get_all_prestations()
        
        self.assertEqual(result, mock_prestations)
        mock_repo.get_all.assert_called_once()

    @patch('app.services.PrestationService.PrestationRepository')
    @patch('app.utils.validate_entity_id')
    def test_get_prestation_by_id(self, mock_validate_id, mock_repo_class):
        """Test récupération prestation par ID"""
        from app.services.PrestationService import PrestationService
        
        valid_id = str(uuid4())
        mock_validate_id.return_value = valid_id

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_prestation = Mock()
        mock_repo.get_by_id.return_value = mock_prestation
        
        service = PrestationService()
        result = service.get_prestation_by_id(valid_id)
        
        self.assertEqual(result, mock_prestation)

    @patch('app.services.PrestationService.PrestationRepository')
    @patch('app.utils.validate_entity_id')
    def test_update_prestation(self, mock_validate_id, mock_repo_class):
        """Test mise à jour prestation"""
        from app.services.PrestationService import PrestationService
        
        valid_id = str(uuid4())
        mock_validate_id.return_value = valid_id

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_repo.get_by_attribute.return_value = None

        mock_prestation = Mock()
        mock_repo.update.return_value = mock_prestation
        
        service = PrestationService()
        result = service.update_prestation(valid_id, name='Nouveau nom')
        
        self.assertEqual(result, mock_prestation)

    @patch('app.services.PrestationService.PrestationRepository')
    @patch('app.services.PrestationService.ReviewRepository')
    @patch('app.utils.validate_entity_id')
    def test_delete_prestation(self, mock_validate_id, mock_review_repo_class, mock_repo_class):
        """Test suppression prestation"""
        from app.services.PrestationService import PrestationService
        
        valid_id = str(uuid4())
        mock_validate_id.return_value = valid_id

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_id.return_value = Mock()  # Prestation existe
        mock_repo.delete.return_value = True

        mock_review_repo = Mock()
        mock_review_repo_class.return_value = mock_review_repo
        mock_review_repo.get_by_prestation_id.return_value = []  # Aucune review liée
        
        service = PrestationService()
        result = service.delete_prestation(valid_id)
        
        self.assertTrue(result)

    @patch('app.services.AppointmentService.AppointmentRepository')
    @patch('app.services.AppointmentService.UserRepository')
    @patch('app.services.AppointmentService.PrestationRepository')
    @patch('app.utils.validate_entity_id')
    def test_get_appointment_by_user_and_prestation_success(self, mock_validate_id, mock_prest_repo, mock_user_repo, mock_appt_repo):
        """Test récupération réussie par utilisateur et prestation"""
        from app.services.AppointmentService import AppointmentService
        
        mock_validate_id.return_value = 'valid-id'
        mock_user_repo.return_value.get_by_id.return_value = Mock()
        mock_prest_repo.return_value.get_by_id.return_value = Mock()
        
        mock_appointment = Mock()
        mock_appt_repo.return_value.get_by_user_and_prestation.return_value = mock_appointment
        
        service = AppointmentService()
        result = service.get_appointment_by_user_and_prestation(str(uuid4()), str(uuid4()))
        
        self.assertEqual(result, mock_appointment)

    @patch('app.services.AppointmentService.AppointmentRepository')
    def test_get_appointments_by_status_invalid(self, mock_appt_repo):
        """Test erreur 400 pour un statut de rendez-vous invalide"""
        from app.services.AppointmentService import AppointmentService
        from app.utils import CustomError
        
        service = AppointmentService()
        with self.assertRaises(CustomError) as cm:
            service.get_appointments_by_status('STATUT_INEXISTANT')
        
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Statut de rendez-vous invalide", str(cm.exception))

    @patch('app.services.AppointmentService.AppointmentRepository')
    @patch('app.utils.validate_entity_id')
    def test_get_appointment_by_id_not_found(self, mock_validate_id, mock_appt_repo):
        """Test erreur 404 si le rendez-vous n'existe pas"""
        from app.services.AppointmentService import AppointmentService
        from app.utils import CustomError
        
        mock_validate_id.return_value = 'valid-id'
        mock_appt_repo.return_value.get_by_id.return_value = None
        
        service = AppointmentService()
        with self.assertRaises(CustomError) as cm:
            service.get_appointment_by_id(str(uuid4()))
        
        self.assertEqual(cm.exception.status_code, 404)

    @patch('app.services.AppointmentService.AppointmentRepository')
    @patch('app.services.AppointmentService.UserRepository')
    @patch('app.utils.validate_entity_id')
    def test_reassign_appointments_from_user_success(self, mock_validate_id, mock_user_repo, mock_appt_repo):
        """Test réassignation réussie des rendez-vous d'un utilisateur à un autre"""
        from app.services.AppointmentService import AppointmentService
        
        mock_validate_id.return_value = 'valid-id'
        mock_user_repo.return_value.get_by_id.side_effect = [Mock(), Mock()] # Old et New user
        
        mock_appointment = Mock()
        mock_appt_repo.return_value.get_by_user_id.return_value = [mock_appointment]
        
        service = AppointmentService()
        result = service.reassign_appointments_from_user(str(uuid4()), str(uuid4()))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_appointment)


if __name__ == '__main__':
    unittest.main()