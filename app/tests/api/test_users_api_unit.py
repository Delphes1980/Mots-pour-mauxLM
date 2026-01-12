#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch


class TestUsersAPIUnit(unittest.TestCase):
    """Tests unitaires purs pour l'API utilisateurs"""

    @patch('app.api.v1.users.facade')
    def test_create_user_success_logic(self, mock_facade):
        """Test logique création utilisateur réussie"""
        mock_user = Mock()
        mock_user.id = 'user-id'
        mock_facade.create_user.return_value = mock_user
        
        user_data = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'jean@example.com',
            'password': 'Password123!'
        }
        
        result = mock_facade.create_user(**user_data)
        
        self.assertEqual(result, mock_user)
        mock_facade.create_user.assert_called_once_with(**user_data)

    @patch('app.api.v1.users.facade')
    def test_get_user_by_id_logic(self, mock_facade):
        """Test logique récupération utilisateur par ID"""
        mock_user = Mock()
        mock_facade.get_user_by_id.return_value = mock_user
        
        result = mock_facade.get_user_by_id('test-id')
        
        self.assertEqual(result, mock_user)
        mock_facade.get_user_by_id.assert_called_once_with('test-id')

    @patch('app.api.v1.users.facade')
    def test_get_all_users_logic(self, mock_facade):
        """Test logique récupération tous utilisateurs"""
        mock_users = [Mock(), Mock()]
        mock_facade.get_all_users.return_value = mock_users
        
        result = mock_facade.get_all_users()
        
        self.assertEqual(result, mock_users)
        mock_facade.get_all_users.assert_called_once()

    @patch('app.api.v1.users.facade')
    def test_update_user_logic(self, mock_facade):
        """Test logique mise à jour utilisateur"""
        mock_user = Mock()
        mock_facade.update_user.return_value = mock_user
        
        update_data = {'first_name': 'Jean Updated'}
        result = mock_facade.update_user('user-id', **update_data)
        
        self.assertEqual(result, mock_user)
        mock_facade.update_user.assert_called_once_with('user-id', **update_data)

    @patch('app.api.v1.users.facade')
    def test_delete_user_logic(self, mock_facade):
        """Test logique suppression utilisateur"""
        mock_facade.delete_user.return_value = True
        
        result = mock_facade.delete_user('user-id')
        
        self.assertTrue(result)
        mock_facade.delete_user.assert_called_once_with('user-id')

    @patch('app.api.v1.users.facade')
    def test_admin_create_user_logic(self, mock_facade):
        """Test logique création utilisateur par l'administrateur"""
        mock_user = Mock()
        mock_facade.admin_create_user.return_value = mock_user
        
        user_data = {
            'first_name': 'Admin',
            'last_name': 'Created',
            'email': 'admin_created@example.com'
        }
        # Le endpoint génère un mot de passe temporaire
        temp_password = 'temp-password'
        
        result = mock_facade.admin_create_user(temp_password, **user_data)
        
        self.assertEqual(result, mock_user)
        mock_facade.admin_create_user.assert_called_once_with(temp_password, **user_data)

    @patch('app.api.v1.users.facade')
    def test_get_user_by_email_logic(self, mock_facade):
        """Test logique récupération utilisateur par mail"""
        mock_user = Mock()
        mock_facade.get_user_by_email.return_value = mock_user
        
        email = 'search@example.com'
        result = mock_facade.get_user_by_email(email)
        
        self.assertEqual(result, mock_user)
        mock_facade.get_user_by_email.assert_called_once_with(email)

    @patch('app.api.v1.users.facade')
    def test_search_users_by_email_fragment_logic(self, mock_facade):
        """Test logique recherche utilisateurs par fragment d'email"""
        mock_users = [Mock(), Mock()]
        mock_facade.search_users_by_email_fragment.return_value = mock_users
        
        fragment = 'jean'
        result = mock_facade.search_users_by_email_fragment(fragment)
        
        self.assertEqual(result, mock_users)
        mock_facade.search_users_by_email_fragment.assert_called_once_with(fragment)

    @patch('app.api.v1.users.facade')
    def test_get_review_by_user_logic(self, mock_facade):
        """Test logique récupération des commentaires de l'utilisateur actuel"""
        mock_reviews = [Mock(), Mock()]
        mock_facade.get_review_by_user.return_value = mock_reviews
        
        user_id = 'user-me'
        result = mock_facade.get_review_by_user(user_id)
        
        self.assertEqual(result, mock_reviews)
        mock_facade.get_review_by_user.assert_called_once_with(user_id)

    @patch('app.api.v1.users.facade')
    def test_admin_reset_password_logic(self, mock_facade):
        """Test logique réinitialisation de mot de passe par l'admin"""
        mock_user = Mock()
        mock_facade.admin_reset_password.return_value = mock_user
        
        user_id = 'user-id'
        temp_password = 'new-temp-password'
        
        result = mock_facade.admin_reset_password(user_id, temp_password)
        
        self.assertEqual(result, mock_user)
        mock_facade.admin_reset_password.assert_called_once_with(user_id, temp_password)

    @patch('app.api.v1.users.facade')
    def test_reset_password_by_email_logic(self, mock_facade):
        """Test logique demande de mot de passe oublié par email"""
        mock_user = Mock()
        mock_facade.reset_password_by_email.return_value = mock_user
        
        email = 'forgot@example.com'
        temp_password = 'temp-pass'
        
        result = mock_facade.reset_password_by_email(email, temp_password)
        
        self.assertEqual(result, mock_user)
        mock_facade.reset_password_by_email.assert_called_once_with(email, temp_password)


if __name__ == '__main__':
    unittest.main()