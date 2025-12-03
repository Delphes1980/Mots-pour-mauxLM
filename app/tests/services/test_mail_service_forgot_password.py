#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
from app.tests.base_test import BaseTest
from app.services.mail_service import send_forgot_password_notification


class TestMailServiceForgotPassword(BaseTest):
    """Tests pour l'envoi d'email de mot de passe oublié - Service"""

    def setUp(self):
        super().setUp()

    @patch('app.services.mail_service.send_mail_async')
    def test_send_forgot_password_notification_success(self, mock_send_mail):
        """Test envoi réussi d'email de mot de passe oublié"""
        user_email = 'test@example.com'
        temp_password = 'TempPass123!'
        
        send_forgot_password_notification(user_email, temp_password)
        
        # Vérifier que send_mail_async a été appelé
        mock_send_mail.assert_called_once()
        
        # Vérifier les détails du message
        call_args = mock_send_mail.call_args[0][0]  # Premier argument (Message object)
        self.assertEqual(call_args.subject, 'Réinitialisation de votre mot de passe')
        self.assertEqual(call_args.recipients, [user_email])
        self.assertIn(temp_password, call_args.body)
        self.assertIn('Bonjour', call_args.body)
        self.assertIn('réinitialisation', call_args.body)

    @patch('app.services.mail_service.send_mail_async')
    def test_send_forgot_password_notification_content(self, mock_send_mail):
        """Test contenu de l'email de mot de passe oublié"""
        user_email = 'user@example.com'
        temp_password = 'NewTemp456!'
        
        send_forgot_password_notification(user_email, temp_password)
        
        call_args = mock_send_mail.call_args[0][0]
        
        # Vérifier le contenu spécifique
        self.assertIn('demande de réinitialisation', call_args.body)
        self.assertIn(temp_password, call_args.body)
        self.assertIn('espace personnel', call_args.body)
        self.assertIn('Mélanie Laborda', call_args.body)
        self.assertIn('contacter immédiatement', call_args.body)

    @patch('app.services.mail_service.send_mail_async')
    def test_send_forgot_password_notification_different_passwords(self, mock_send_mail):
        """Test avec différents mots de passe temporaires"""
        user_email = 'test@example.com'
        passwords = [
            'TempPass123!',
            'NewSecure456@',
            'Reset#789',
            'Forgot$Pass1'
        ]
        
        for temp_password in passwords:
            mock_send_mail.reset_mock()
            
            send_forgot_password_notification(user_email, temp_password)
            
            mock_send_mail.assert_called_once()
            call_args = mock_send_mail.call_args[0][0]
            self.assertIn(temp_password, call_args.body)

    @patch('app.services.mail_service.send_mail_async')
    def test_send_forgot_password_notification_different_emails(self, mock_send_mail):
        """Test avec différentes adresses email"""
        temp_password = 'TempPass123!'
        emails = [
            'user1@example.com',
            'admin@test.com',
            'client@domain.org',
            'test.user@company.co.uk'
        ]
        
        for user_email in emails:
            mock_send_mail.reset_mock()
            
            send_forgot_password_notification(user_email, temp_password)
            
            mock_send_mail.assert_called_once()
            call_args = mock_send_mail.call_args[0][0]
            self.assertEqual(call_args.recipients, [user_email])

    @patch('app.services.mail_service.send_mail_async')
    @patch('app.services.mail_service.current_app.config')
    def test_send_forgot_password_notification_sender_config(self, mock_config, mock_send_mail):
        """Test configuration de l'expéditeur"""
        mock_config.get.return_value = 'noreply@example.com'
        
        user_email = 'test@example.com'
        temp_password = 'TempPass123!'
        
        send_forgot_password_notification(user_email, temp_password)
        
        mock_config.get.assert_called_with('MAIL_DEFAULT_SENDER')
        call_args = mock_send_mail.call_args[0][0]
        self.assertEqual(call_args.sender, 'noreply@example.com')

    @patch('app.services.mail_service.send_mail_async')
    def test_send_forgot_password_notification_message_structure(self, mock_send_mail):
        """Test structure du message"""
        user_email = 'test@example.com'
        temp_password = 'TempPass123!'
        
        send_forgot_password_notification(user_email, temp_password)
        
        call_args = mock_send_mail.call_args[0][0]
        
        # Vérifier la structure du message
        self.assertIsNotNone(call_args.subject)
        self.assertIsNotNone(call_args.body)
        self.assertIsNotNone(call_args.sender)
        self.assertIsNotNone(call_args.recipients)
        
        # Vérifier que le body n'est pas vide
        self.assertTrue(len(call_args.body.strip()) > 0)
        
        # Vérifier que le subject n'est pas vide
        self.assertTrue(len(call_args.subject.strip()) > 0)

    @patch('app.services.mail_service.send_mail_async', side_effect=Exception('Mail server error'))
    def test_send_forgot_password_notification_mail_failure(self, mock_send_mail):
        """Test gestion d'erreur lors de l'envoi d'email"""
        user_email = 'test@example.com'
        temp_password = 'TempPass123!'
        
        # L'exception doit être propagée
        with self.assertRaises(Exception) as context:
            send_forgot_password_notification(user_email, temp_password)
        
        self.assertIn('Mail server error', str(context.exception))

    @patch('app.services.mail_service.send_mail_async')
    def test_send_forgot_password_notification_security_content(self, mock_send_mail):
        """Test contenu de sécurité dans l'email"""
        user_email = 'test@example.com'
        temp_password = 'TempPass123!'
        
        send_forgot_password_notification(user_email, temp_password)
        
        call_args = mock_send_mail.call_args[0][0]
        
        # Vérifier les mentions de sécurité
        body_lower = call_args.body.lower()
        self.assertIn('si vous n\'êtes pas à l\'origine', body_lower)
        self.assertIn('contacter', body_lower)
        self.assertIn('immédiatement', body_lower)

    @patch('app.services.mail_service.send_mail_async')
    def test_send_forgot_password_notification_professional_tone(self, mock_send_mail):
        """Test ton professionnel de l'email"""
        user_email = 'test@example.com'
        temp_password = 'TempPass123!'
        
        send_forgot_password_notification(user_email, temp_password)
        
        call_args = mock_send_mail.call_args[0][0]
        
        # Vérifier le ton professionnel
        self.assertIn('Bonjour', call_args.body)
        self.assertIn('Cordialement', call_args.body)
        self.assertIn('Mélanie Laborda', call_args.body)
        
        # Vérifier l'absence de ton trop familier
        body_lower = call_args.body.lower()
        self.assertNotIn('salut', body_lower)
        self.assertNotIn('ciao', body_lower)


if __name__ == '__main__':
    unittest.main()