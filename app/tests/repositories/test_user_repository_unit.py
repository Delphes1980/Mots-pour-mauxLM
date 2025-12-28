#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch


class TestUserRepositoryUnit(unittest.TestCase):
    """Tests unitaires purs pour UserRepository"""

    @patch('app.db')
    def test_search_by_email_fragment(self, mock_db):
        """Test recherche par fragment d'email"""
        from app.persistence.UserRepository import UserRepository
        
        mock_users = [Mock(), Mock()]
        mock_session = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_users
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = UserRepository()
        result = repo.search_by_email_fragment('test')
        
        self.assertEqual(result, mock_users)
        mock_query.filter.assert_called_once()

    @patch('app.db')
    @patch('app.persistence.UserRepository.name_validation')
    @patch('app.persistence.UserRepository.email_validation')
    @patch('app.persistence.UserRepository.validate_password')
    @patch('app.persistence.UserRepository.address_validation')
    @patch('app.persistence.UserRepository.validate_phone_number')
    def test_create_user_success(self, mock_phone, mock_addr, mock_pass, mock_email, mock_name, mock_db):
        """Test création utilisateur réussie"""
        from app.persistence.UserRepository import UserRepository
        
        # Configuration des mocks de validation
        mock_name.side_effect = lambda x, _: x
        mock_email.return_value = 'test@test.com'
        mock_pass.return_value = 'hashed_Password1'
        mock_addr.return_value = '123 Rue Test'
        mock_phone.return_value = '1234567890'
        
        mock_session = Mock()
        mock_db.session = mock_session
        
        repo = UserRepository()
        repo.get_by_attribute = Mock(return_value=None) # L'utilisateur n'existe pas
        
        result = repo.create_user('Jean', 'Dupont', 'test@test.com', 'Password123!')
        
        self.assertEqual(result.email, 'test@test.com')
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('app.db')
    @patch('app.persistence.UserRepository.name_validation')
    @patch('app.persistence.UserRepository.email_validation')
    @patch('app.persistence.UserRepository.validate_password')
    def test_create_user_already_exists(self, mock_pass, mock_email, mock_name, mock_db):
        """Test erreur si l'email existe déjà"""
        from app.persistence.UserRepository import UserRepository
        
        mock_name.side_effect = lambda x, _: x
        mock_email.return_value = 'exists@test.com'
        mock_pass.return_value = 'valid_password'

        repo = UserRepository()
        repo.get_by_attribute = Mock(return_value=Mock()) # Simule email trouvé
        
        with self.assertRaises(ValueError) as cm:
            repo.create_user('Jean', 'Dupont', 'exists@test.com', 'Password123!')
            
        self.assertIn("Un utilisateur avec cet email existe déjà", str(cm.exception))

    @patch('app.db')
    @patch('app.persistence.UserRepository.name_validation')
    @patch('app.persistence.UserRepository.email_validation')
    @patch('app.persistence.UserRepository.validate_password')
    @patch('app.persistence.UserRepository.address_validation')
    @patch('app.persistence.UserRepository.validate_phone_number')
    def test_admin_create_user_success(self, mock_phone, mock_addr, mock_pass, mock_email, mock_name, mock_db):
        """Test création utilisateur par admin"""
        from app.persistence.UserRepository import UserRepository
        
        mock_name.side_effect = lambda x, _: x
        mock_email.return_value = 'new@text.com'
        mock_pass.return_value = 'hashed_Password1'
        mock_addr.return_value = '123 Rue Test'
        mock_phone.return_value = '1234567890'

        mock_session = Mock()
        mock_db.session = mock_session
        
        repo = UserRepository()
        repo.get_by_attribute = Mock(return_value=None)
        
        result = repo.admin_create_user(
            first_name='Admin', 
            last_name='User', 
            email='new@test.com', 
            password='TempPassword123!'
        )
        
        self.assertEqual(result.first_name, 'Admin')
        mock_session.commit.assert_called_once()

    @patch('app.db')
    def test_admin_create_user_missing_password(self, mock_db):
        """Test erreur si mot de passe manquant en création admin"""
        from app.persistence.UserRepository import UserRepository
        
        repo = UserRepository()
        repo.get_by_attribute = Mock(return_value=None)
        
        with self.assertRaises(ValueError) as cm:
            repo.admin_create_user('Jean', 'Dupont', 'test@test.com', password=None)
            
        self.assertIn("Mot de passe temporaire manquant", str(cm.exception))

    @patch('app.db')
    def test_create_wrapper(self, mock_db):
        """Test que create() redirige vers create_user()"""
        from app.persistence.UserRepository import UserRepository
        
        repo = UserRepository()
        repo.create_user = Mock(return_value="success")
        
        result = repo.create(first_name='Jean', email='test@test.com')
        
        repo.create_user.assert_called_once()
        self.assertEqual(result, "success")


if __name__ == '__main__':
    unittest.main()