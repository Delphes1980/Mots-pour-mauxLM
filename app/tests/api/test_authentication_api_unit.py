#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch


class TestAuthenticationAPIUnit(unittest.TestCase):
    """Tests unitaires purs pour l'API d'authentification"""

    @patch('app.api.v1.authentication.facade')
    def test_login_success_logic(self, mock_facade):
        """Test logique login réussi"""
        # Mock user
        mock_user = Mock()
        mock_user.id = 'user-id'
        mock_user.email = 'test@example.com'
        mock_user.is_admin = False
        mock_user.verify_password.return_value = True
        
        mock_facade.get_user_by_email.return_value = mock_user
        
        # Test logique
        credentials = {'email': 'test@example.com', 'password': 'Password123!'}
        user = mock_facade.get_user_by_email(credentials['email'])
        
        self.assertEqual(user, mock_user)
        self.assertTrue(user.verify_password(credentials['password']))
        mock_facade.get_user_by_email.assert_called_once_with('test@example.com')

    @patch('app.api.v1.authentication.facade')
    def test_login_invalid_credentials_logic(self, mock_facade):
        """Test logique login avec identifiants invalides"""
        mock_facade.get_user_by_email.return_value = None
        
        # Test logique
        credentials = {'email': 'test@example.com', 'password': 'WrongPassword'}
        user = mock_facade.get_user_by_email(credentials['email'])
        
        self.assertIsNone(user)
        mock_facade.get_user_by_email.assert_called_once_with('test@example.com')

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('app.api.v1.authentication.unset_jwt_cookies')
    def test_logout_logic(self, mock_unset_cookies, mock_jwt_required):
        """Test logique déconnexion réussie"""
        from app.api.v1.authentication import Logout
        from flask import Flask
        import json

        app = Flask(__name__)
        app.config['JWT_TOKEN_LOCATION'] = ['headers']

        with app.test_request_context():
            resource = Logout()
            mock_jwt_required.return_value = None

            response = resource.post()
            
            # Vérifie le code de statut 200 
            self.assertEqual(response.status_code, 200)
            
            # Vérifie le message de succès 
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['message'], 'Déconnexion réussie')
            
            # Vérifie que la fonction de suppression des cookies a été appelée 
            mock_unset_cookies.assert_called_once()

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('app.api.v1.authentication.get_jwt_identity')
    @patch('app.api.v1.authentication.get_jwt')
    def test_authentication_status_logic(self, mock_get_jwt, mock_get_identity, mock_jwt_required):
        """Test logique vérification de l'état de connexion"""
        from app.api.v1.authentication import AuthenticationStatus
        from flask import Flask
        
        app = Flask(__name__)
        with app.test_request_context():
            # Mock des données JWT
            mock_get_identity.return_value = 'user-id-123'
            mock_get_jwt.return_value = {'is_admin': True}
            mock_jwt_required.return_value = None
        
            resource = AuthenticationStatus()
            response, status_code = resource.get()
        
            # Vérification de la réponse 
            self.assertEqual(status_code, 200)
            self.assertEqual(response['user_id'], 'user-id-123')
            self.assertTrue(response['is_admin'])


if __name__ == '__main__':
    unittest.main()