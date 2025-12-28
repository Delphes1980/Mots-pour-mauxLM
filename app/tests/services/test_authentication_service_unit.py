#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
from app.utils import CustomError


class TestAuthenticationServiceUnit(unittest.TestCase):
    """Tests unitaires complets pour AuthenticationService"""

    @patch('app.services.AuthenticationService.UserRepository')
    @patch('app.services.AuthenticationService.verify_password')
    @patch('app.services.AuthenticationService.create_access_token')
    @patch('app.utils.validate_password')
    @patch('app.utils.email_validation')
    def test_login_success(self, mock_email, mock_val_pass, mock_token, mock_verify, mock_repo_class):
        """Test login réussi"""
        from app.services.AuthenticationService import AuthenticationService
        
        mock_val_pass.return_value = None
        mock_email.return_value = None
        mock_user = Mock()
        mock_user.id = str(uuid4())
        mock_user.password = 'hashed'
        mock_user.is_admin = False

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_attribute.return_value = mock_user
        
        mock_verify.return_value = True
        mock_token.return_value = 'jwt_token'
        
        service = AuthenticationService()
        result = service.login('test@example.com', 'Password123!')
        
        self.assertEqual(result, 'jwt_token')

    @patch('app.services.AuthenticationService.UserRepository')
    @patch('app.utils.validate_password')
    def test_login_user_not_found(self, mock_val_pass, mock_repo_class):
        """Test login utilisateur non trouvé"""
        from app.services.AuthenticationService import AuthenticationService
        
        mock_val_pass.return_value = None
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_attribute.return_value = None
        
        service = AuthenticationService()
        
        with self.assertRaises(CustomError):
            service.login('test@example.com', 'Password123!')

    @patch('app.services.AuthenticationService.UserRepository')
    @patch('app.bcrypt.check_password_hash')
    def test_login_wrong_password(self, mock_hash, mock_repo_class):
        """Test login mot de passe incorrect"""
        from app.services.AuthenticationService import AuthenticationService
        from app.utils import CustomError
        
        mock_user = Mock()
        mock_user.password = 'hashed_password'
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_attribute.return_value = mock_user
        
        mock_hash.return_value = False
        
        service = AuthenticationService()
        
        with self.assertRaises(CustomError):
            service.login('test@example.com', 'wrong_password')

    @patch('app.services.AuthenticationService.UserRepository')
    @patch('app.bcrypt.check_password_hash')
    @patch('app.bcrypt.generate_password_hash')
    @patch('app.utils.validate_password')
    def test_change_password(self, mock_val_pass, mock_gen_hash, mock_check_hash, mock_repo_class):
        """Test changement mot de passe"""
        from app.services.AuthenticationService import AuthenticationService
        
        mock_val_pass.return_value = None
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_id.return_value = mock_user
        mock_repo.update.return_value = mock_user
        
        mock_check_hash.return_value = True
        mock_gen_hash.return_value = b'new_hashed'
        
        service = AuthenticationService()
        result = service.change_password(str(uuid4()), 'OldPpassword123!', 'NewPassword123!')
        
        self.assertEqual(result, mock_user)

    @patch('app.services.AuthenticationService.UserRepository')
    @patch('app.services.AuthenticationService.validate_entity_id')
    @patch('app.services.AuthenticationService.validate_password')
    def test_admin_reset_password(self, mock_val_pass, mock_val_id, mock_repo_class):
        """Test réinitialisation admin du mot de passe"""
        from app.services.AuthenticationService import AuthenticationService
        
        mock_val_id.return_value = None
        mock_val_pass.return_value = None
        
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_id.return_value = mock_user
        mock_repo.update.return_value = mock_user
        
        service = AuthenticationService()
        result = service.admin_reset_password(str(uuid4()), 'NewPass123!')
        
        self.assertEqual(result, mock_user)
        mock_repo.update.assert_called_once()

    @patch('app.services.AuthenticationService.UserRepository')
    @patch('app.services.AuthenticationService.email_validation')
    @patch('app.services.AuthenticationService.validate_password')
    def test_reset_password_by_email(self, mock_val_pass, mock_email_val, mock_repo_class):
        """Test réinitialisation par email"""
        from app.services.AuthenticationService import AuthenticationService
        
        mock_email_val.return_value = None
        mock_val_pass.return_value = None
        
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_attribute.return_value = mock_user
        mock_repo.update.return_value = mock_user
        
        service = AuthenticationService()
        result = service.reset_password_by_email('test@example.com', 'TempPass123!')
        
        self.assertEqual(result, mock_user)


if __name__ == '__main__':
    unittest.main()