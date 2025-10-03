import unittest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from flask_mail import Message
from app.services.mail_service import send_mail_async, send_appointment_notifications


class TestMailService(unittest.TestCase):
    """Tests pour le service mail"""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['MAIL_USERNAME'] = 'test@example.com'
        self.app.config['MAIL_SERVER'] = 'localhost'
        self.app.config['MAIL_PORT'] = 587
        self.app.config['MAIL_USE_TLS'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('app.services.mail_service.mail')
    def test_send_mail_async_success(self, mock_mail):
        """Test envoi email réussi"""
        mock_message = Mock(spec=Message)
        
        send_mail_async(mock_message)
        
        mock_mail.send.assert_called_once_with(mock_message)

    @patch('app.services.mail_service.mail')
    @patch('app.services.mail_service.current_app')
    def test_send_mail_async_failure(self, mock_current_app, mock_mail):
        """Test gestion d'erreur lors de l'envoi"""
        mock_message = Mock()
        mock_mail.send.side_effect = Exception("SMTP Error")
        mock_logger = Mock()
        mock_current_app.logger = mock_logger
        
        with self.assertRaises(Exception):
            send_mail_async(mock_message)
        
        mock_logger.error.assert_called_once_with("Erreur lors de l'envoi de l'e-mail : SMTP Error")

    @patch('app.services.mail_service.send_mail_async')
    @patch('flask.current_app')
    def test_send_appointment_notifications_success(self, mock_current_app, mock_send_async):
        """Test envoi notifications rendez-vous réussi"""
        mock_current_app.config.get.return_value = "sender@example.com"
        
        context = {
            'user_full_name': 'John Doe',
            'prestation_name': 'Massage',
            'message': 'Je souhaite un rendez-vous'
        }
        
        send_appointment_notifications(
            user_email="user@example.com",
            practitioner_email="practitioner@example.com",
            **context
        )
        
        # Vérifier que send_mail_async a été appelé 2 fois (praticien + utilisateur)
        self.assertEqual(mock_send_async.call_count, 2)
        
        # Vérifier les arguments des appels
        calls = mock_send_async.call_args_list
        
        # Premier appel (praticien)
        practitioner_msg = calls[0][0][0]
        self.assertIn("Nouvelle demande", practitioner_msg.subject)
        self.assertEqual(practitioner_msg.recipients, ["practitioner@example.com"])
        self.assertIn("John Doe", practitioner_msg.body)
        
        # Deuxième appel (utilisateur)
        user_msg = calls[1][0][0]
        self.assertIn("Confirmation", user_msg.subject)
        self.assertEqual(user_msg.recipients, ["user@example.com"])
        self.assertIn("John Doe", user_msg.body)

    @patch('app.services.mail_service.send_mail_async')
    @patch('flask.current_app')
    def test_send_appointment_notifications_content(self, mock_current_app, mock_send_async):
        """Test contenu des notifications"""
        mock_current_app.config.get.return_value = "sender@example.com"
        
        context = {
            'user_full_name': 'Marie Martin',
            'prestation_name': 'Thérapie',
            'message': 'Besoin d\'aide urgente'
        }
        
        send_appointment_notifications(
            user_email="marie@example.com",
            practitioner_email="melanie@example.com",
            **context
        )
        
        calls = mock_send_async.call_args_list
        
        # Vérifier contenu message praticien
        practitioner_msg = calls[0][0][0]
        self.assertIn("Marie Martin", practitioner_msg.body)
        self.assertIn("marie@example.com", practitioner_msg.body)
        self.assertIn("Thérapie", practitioner_msg.body)
        self.assertIn("Besoin d'aide urgente", practitioner_msg.body)
        
        # Vérifier contenu message utilisateur
        user_msg = calls[1][0][0]
        self.assertIn("Marie Martin", user_msg.body)
        self.assertIn("Thérapie", user_msg.body)
        self.assertIn("Mélanie Laborda", user_msg.body)



    @patch('app.services.mail_service.send_mail_async')
    @patch('flask.current_app')
    def test_send_appointment_notifications_special_characters(self, mock_current_app, mock_send_async):
        """Test avec caractères spéciaux dans le contenu"""
        mock_current_app.config.get.return_value = "sender@example.com"
        
        context = {
            'user_full_name': 'Jean-François Müller',
            'prestation_name': 'Thérapie énergétique',
            'message': 'J\'ai besoin d\'une séance à 14h30'
        }
        
        send_appointment_notifications(
            user_email="jean@example.com",
            practitioner_email="practitioner@example.com",
            **context
        )
        
        calls = mock_send_async.call_args_list
        
        # Vérifier que les caractères spéciaux sont préservés
        practitioner_msg = calls[0][0][0]
        self.assertIn("Jean-François Müller", practitioner_msg.body)
        self.assertIn("Thérapie énergétique", practitioner_msg.body)
        self.assertIn("14h30", practitioner_msg.body)


if __name__ == '__main__':
    unittest.main()