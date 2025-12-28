#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
from app.utils import CustomError


class TestUserServiceUnit(unittest.TestCase):
    """Tests unitaires complets pour UserService"""

    @patch('app.services.UserService.UserRepository')
    @patch('app.utils.email_validation')
    @patch('app.utils.name_validation')
    @patch('app.utils.validate_password')
    def test_create_user_success(self, mock_pass_val, mock_name_val, mock_email_val, mock_repo_class):
        """Test création utilisateur réussie"""
        from app.services.UserService import UserService
        
        mock_email_val.return_value = 'test@example.com'
        mock_name_val.side_effect = lambda x, _: x
        mock_pass_val.return_value = 'Password123!'
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_attribute.return_value = None
        mock_user = Mock()
        mock_repo.create_user.return_value = mock_user
        
        service = UserService()
        user_data = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'test@example.com',
            'password': 'Password123!',
            'address': '123 Rue de la Ville',
            'phone_number': '1234567890',
            'is_admin': False
        }
        result = service.create_user(**user_data)
        
        self.assertEqual(result, mock_user)

    @patch('app.services.UserService.UserRepository')
    @patch('app.utils.email_validation')
    @patch('app.utils.name_validation')
    @patch('app.utils.validate_password')
    @patch('app.utils.address_validation')
    @patch('app.utils.validate_phone_number')
    def test_create_user_email_exists(self, mock_phone, mock_addr, mock_pass, mock_name, mock_email, mock_repo_class):
        """Test création utilisateur email existant"""
        from app.services.UserService import UserService
        from app.utils import CustomError
        
        mock_email.return_value = 'test@example.com'
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_attribute.return_value = Mock()
        
        service = UserService()
        
        with self.assertRaises(CustomError) as context:
            service.create_user(
                first_name='Jean',
                last_name='Dupont',
                email='test@example.com',
                password='Password123!',
                address='123 rue du test',
                phone_number='1234567890',
            )
        self.assertEqual(context.exception.status_code, 409)
        self.assertIn("Email already exists", str(context.exception))

    @patch('app.services.UserService.UserRepository')
    def test_get_user_by_id(self, mock_repo_class):
        """Test récupération utilisateur par ID"""
        from app.services.UserService import UserService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_user = Mock()
        mock_repo.get_by_id.return_value = mock_user
        
        service = UserService()
        result = service.get_user_by_id(str(uuid4()))
        
        self.assertEqual(result, mock_user)

    @patch('app.services.UserService.UserRepository')
    def test_get_all_users(self, mock_repo_class):
        """Test récupération tous utilisateurs"""
        from app.services.UserService import UserService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_users = [Mock(), Mock()]
        mock_repo.get_all.return_value = mock_users
        
        service = UserService()
        result = service.get_all_users()
        
        self.assertEqual(result, mock_users)

    @patch('app.services.UserService.UserRepository')
    def test_update_user(self, mock_repo_class):
        """Test mise à jour utilisateur"""
        from app.services.UserService import UserService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_user = Mock()
        mock_repo.update.return_value = mock_user
        
        service = UserService()
        result = service.update_user(str(uuid4()), first_name='Jean')
        
        self.assertEqual(result, mock_user)

    @patch('app.services.UserService.UserRepository')
    @patch('app.services.UserService.ReviewRepository')
    @patch('app.services.UserService.AppointmentRepository')
    def test_delete_user(self, mock_appt_repo_class, mock_review_class, mock_repo_class):
        """Test suppression utilisateur"""
        from app.services.UserService import UserService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.delete.return_value = True

        mock_review_repo = Mock()
        mock_review_class.return_value = mock_review_repo
        mock_review_repo.get_by_user_id.return_value = []

        mock_appt_repo = Mock()
        mock_appt_repo_class.return_value = mock_appt_repo
        mock_appt_repo.get_by_user_id.return_value = []
        
        service = UserService()
        result = service.delete_user(str(uuid4()))
        
        self.assertTrue(result)

    @patch('app.services.UserService.UserRepository')
    def test_get_user_by_email(self, mock_repo_class):
        """Test récupération utilisateur par email"""
        from app.services.UserService import UserService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_user = Mock()
        mock_repo.get_by_attribute.return_value = mock_user
        
        service = UserService()
        result = service.get_user_by_email('test@example.com')
        
        self.assertEqual(result, mock_user)

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
        result = service.admin_create_user(
            'TempPass123!', 
            first_name='Admin', 
            last_name='User', 
            email='admin@test.com'
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
        """Test recherche par fragment ne retournant aucun résultat"""
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
    @patch('app.services.UserService.ReviewRepository')
    @patch('app.services.UserService.AppointmentRepository')
    def test_delete_user_with_reassignment_logic(self, mock_appt_repo_class, mock_review_repo_class, mock_repo_class):
        """Test vérifiant que la suppression réassigne bien les données au Ghost User"""
        from app.services.UserService import UserService
        
        # Setup UserRepository
        mock_user_repo = Mock()
        mock_repo_class.return_value = mock_user_repo
        
        # L'utilisateur à supprimer
        user_to_del = Mock(id=str(uuid4()), email='user@test.com')
        # Le Ghost User système
        ghost_user = Mock(id=str(uuid4()), email='deleted@system.local')
        
        mock_user_repo.get_by_id.return_value = user_to_del
        mock_user_repo.get_by_attribute.return_value = ghost_user
        
        # Setup Review et Appointment repositories pour simuler des données existantes
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