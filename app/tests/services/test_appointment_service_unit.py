#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
from app.utils import CustomError


class TestAppointmentServiceUnit(unittest.TestCase):
    """Tests unitaires complets pour AppointmentService"""
    @patch('app.services.AppointmentService.AppointmentRepository')
    @patch('app.services.AppointmentService.UserRepository')
    @patch('app.services.AppointmentService.PrestationRepository')
    @patch('app.services.AppointmentService.send_appointment_notifications')
    @patch('app.utils.text_field_validation')
    @patch('app.utils.validate_entity_id')
    def test_create_appointment_success(self, mock_validate_id, mock_text_val, mock_mail, mock_prest_repo, mock_user_repo, mock_appt_repo):
        """Test création appointment réussie"""
        from app.services.AppointmentService import AppointmentService
        fake_app = Mock()
        fake_app.config.get.return_value = "practitioner@example.com"

        with patch('app.services.AppointmentService.current_app', new=fake_app):
            mock_text_val.return_value = None
            mock_validate_id.return_value = 'valid-id'
            mock_mail.return_value = None
        
            mock_user = Mock()
            mock_prestation = Mock()
            mock_user_repo.return_value.get_by_id.return_value = mock_user
            mock_prest_repo.return_value.get_by_id.return_value = mock_prestation
        
            mock_appointment = Mock()
            mock_appt_repo.return_value.create_appointment.return_value = mock_appointment
        
            service = AppointmentService()
            result = service.create_appointment(
                message='Message',
                user_id=str(uuid4()),
                prestation_id=str(uuid4())
            )
        
            self.assertEqual(result, mock_appointment)

    @patch('app.services.AppointmentService.AppointmentRepository')
    @patch('app.utils.validate_entity_id')
    def test_get_appointment_by_id(self, mock_validate_id, mock_repo_class):
        """Test récupération appointment par ID"""
        from app.services.AppointmentService import AppointmentService
        
        mock_validate_id.return_value = 'valid-id'
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_appointment = Mock()
        mock_repo.get_by_id.return_value = mock_appointment
        
        service = AppointmentService()
        result = service.get_appointment_by_id(str(uuid4()))
        
        self.assertEqual(result, mock_appointment)

    @patch('app.services.AppointmentService.AppointmentRepository')
    def test_get_all_appointments(self, mock_repo_class):
        """Test récupération tous appointments"""
        from app.services.AppointmentService import AppointmentService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_appointments = [Mock(), Mock()]
        mock_repo.get_all.return_value = mock_appointments
        
        service = AppointmentService()
        result = service.get_all_appointments()
        
        self.assertEqual(result, mock_appointments)

    @patch('app.services.AppointmentService.AppointmentRepository')
    @patch('app.services.AppointmentService.UserRepository')
    @patch('app.utils.validate_entity_id')
    def test_get_appointment_by_user(self, mock_validate_id, mock_user_repo, mock_repo_class):
        """Test récupération appointments par utilisateur"""
        from app.services.AppointmentService import AppointmentService
        
        mock_validate_id.return_value = 'valid-id'
        mock_user = Mock()
        mock_user_repo.return_value.get_by_id.return_value = mock_user
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_appointments = [Mock(), Mock()]
        mock_repo.get_by_user_id.return_value = mock_appointments
        
        service = AppointmentService()
        result = service.get_appointment_by_user(str(uuid4()))
        
        self.assertEqual(result, mock_appointments)

    @patch('app.services.AppointmentService.AppointmentRepository')
    @patch('app.services.AppointmentService.PrestationRepository')
    @patch('app.utils.validate_entity_id')
    def test_get_appointment_by_prestation(self, mock_validate_id, mock_prest_repo, mock_repo_class):
        """Test récupération appointments par prestation"""
        from app.services.AppointmentService import AppointmentService
        
        mock_validate_id.return_value = 'valid-id'
        mock_prestation = Mock()
        mock_prest_repo.return_value.get_by_id.return_value = mock_prestation
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_appointments = [Mock(), Mock()]
        mock_repo.get_by_prestation_id.return_value = mock_appointments
        
        service = AppointmentService()
        result = service.get_appointment_by_prestation(str(uuid4()))
        
        self.assertEqual(result, mock_appointments)

    @patch('app.services.AppointmentService.AppointmentRepository')
    def test_get_appointments_by_status(self, mock_repo_class):
        """Test récupération appointments par statut"""
        from app.services.AppointmentService import AppointmentService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_appointments = [Mock(), Mock()]
        mock_repo.get_appointments_by_status.return_value = mock_appointments
        
        service = AppointmentService()
        result = service.get_appointments_by_status('PENDING')
        
        self.assertEqual(result, mock_appointments)

    @patch('app.services.AppointmentService.AppointmentRepository')
    @patch('app.services.AppointmentService.UserRepository')
    @patch('app.services.AppointmentService.PrestationRepository')
    @patch('app.services.AppointmentService.send_appointment_status_notification')
    @patch('app.utils.validate_entity_id')
    def test_update_appointment_status(self, mock_validate_id, mock_mail, mock_prest_repo, mock_user_repo, mock_repo_class):
        """Test mise à jour statut appointment"""
        from app.services.AppointmentService import AppointmentService
        
        mock_validate_id.return_value = 'valid-id'
        mock_mail.return_value = None

        valid_uid = str(uuid4())
        mock_appointment = Mock()
        mock_appointment.user_id = valid_uid
        mock_appointment.prestation_id = valid_uid
        
        mock_user = Mock()
        mock_prestation = Mock()
        mock_user_repo.return_value.get_by_id.return_value = mock_user
        mock_prest_repo.return_value.get_by_id.return_value = mock_prestation
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_id.return_value = mock_appointment
        mock_repo.update.return_value = mock_appointment
        
        service = AppointmentService()
        result = service.update_appointment_status(str(uuid4()), status='CONFIRMED')
        
        self.assertEqual(result, mock_appointment)
        mock_mail.assert_called_once()

    @patch('app.services.AppointmentService.AppointmentRepository')
    @patch('app.utils.validate_entity_id')
    def test_delete_appointment(self, mock_validate_id, mock_repo_class):
        """Test suppression appointment"""
        from app.services.AppointmentService import AppointmentService
        
        mock_validate_id.return_value = 'valid-id'
        mock_appointment = Mock()
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_id.return_value = mock_appointment
        mock_repo.delete.return_value = True
        
        service = AppointmentService()
        result = service.delete_appointment(str(uuid4()))
        
        self.assertTrue(result)

    @patch('app.services.UserService.UserRepository')
    @patch('app.utils.validate_init_args')
    @patch('app.utils.name_validation')
    @patch('app.utils.email_validation')
    @patch('app.utils.address_validation')
    @patch('app.utils.validate_phone_number')
    @patch('app.utils.admin_validation')
    def test_admin_create_user_success(self, mock_admin, mock_phone, mock_addr, mock_email, mock_name, mock_init, mock_repo_class):
        """Test création utilisateur par admin avec mot de passe temporaire"""
        from app.services.UserService import UserService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_attribute.return_value = None
        mock_user = Mock()
        mock_repo.admin_create_user.return_value = mock_user
        
        service = UserService()
        # admin_create_user prend temp_password en premier argument 
        result = service.admin_create_user(
            'TempPass123!', 
            first_name='Admin', 
            last_name='User', 
            email='admin@test.com',
            address='Test',
            phone_number='1234567890'
        )
        
        self.assertEqual(result, mock_user)
        mock_repo.admin_create_user.assert_called_once()

    @patch('app.services.UserService.UserRepository')
    def test_search_users_by_email_fragment_success(self, mock_repo_class):
        """Test recherche réussie par fragment d'email"""
        from app.services.UserService import UserService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_list = [Mock(), Mock()]
        mock_repo.search_by_email_fragment.return_value = mock_list
        
        service = UserService()
        result = service.search_users_by_email_fragment('jean')
        
        self.assertEqual(result, mock_list)

    @patch('app.services.UserService.UserRepository')
    def test_search_users_by_email_fragment_not_found(self, mock_repo_class):
        """Test recherche par fragment ne retournant aucun résultat (404)"""
        from app.services.UserService import UserService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.search_by_email_fragment.return_value = []
        
        service = UserService()
        with self.assertRaises(CustomError) as cm:
            service.search_users_by_email_fragment('inconnu')
        
        self.assertEqual(cm.exception.status_code, 404)

    @patch('app.services.UserService.UserRepository')
    def test_get_user_by_id_not_found(self, mock_repo_class):
        """Test erreur 404 si l'utilisateur n'existe pas"""
        from app.services.UserService import UserService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_id.return_value = None
        
        service = UserService()
        with self.assertRaises(CustomError) as cm:
            service.get_user_by_id(str(uuid4()))
        
        self.assertEqual(cm.exception.status_code, 404)

    @patch('app.services.UserService.UserRepository')
    def test_delete_ghost_user_forbidden(self, mock_repo_class):
        """Test interdiction de supprimer le compte système ghost (403)"""
        from app.services.UserService import UserService
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        ghost = Mock()
        ghost.email = 'deleted@system.local'
        mock_repo.get_by_id.return_value = ghost
        
        service = UserService()
        with self.assertRaises(CustomError) as cm:
            service.delete_user(str(uuid4()))
        
        self.assertEqual(cm.exception.status_code, 403)

    @patch('app.services.UserService.UserRepository')
    @patch('app.services.UserService.ReviewRepository')
    @patch('app.services.UserService.AppointmentRepository')
    def test_delete_user_with_reassignment_logic(self, mock_appt_repo_class, mock_review_repo_class, mock_repo_class):
        """Test vérifiant que la suppression réassigne bien les données au Ghost User"""
        from app.services.UserService import UserService
        
        mock_user_repo = Mock()
        mock_repo_class.return_value = mock_user_repo
        
        user_to_del = Mock(id=str(uuid4()), email='user@test.com')
        ghost_user = Mock(id=str(uuid4()), email='deleted@system.local')
        
        mock_user_repo.get_by_id.return_value = user_to_del
        mock_user_repo.get_by_attribute.return_value = ghost_user
        
        mock_rev_repo = Mock()
        mock_review_repo_class.return_value = mock_rev_repo
        mock_rev_repo.get_by_user_id.return_value = [Mock()]
        
        mock_appt_repo = Mock()
        mock_appt_repo_class.return_value = mock_appt_repo
        mock_appt_repo.get_by_user_id.return_value = [Mock()]
        
        service = UserService()
        service.delete_user(user_to_del.id)
        
        # On vérifie que les méthodes de réassignation ont été appelées 
        mock_rev_repo.reassign_reviews_from_user.assert_called_once()
        mock_appt_repo.reassign_appointments_from_user.assert_called_once()


if __name__ == '__main__':
    unittest.main()