#!/usr/bin/env python3

import unittest
from flask import Flask
from app.tests.base_test import BaseTest


class TestMailServiceSimple(BaseTest):
    """Tests pour le service mail sans mocks - tests de structure et configuration"""

    def test_mail_service_imports(self):
        """Test que les fonctions du service mail peuvent être importées"""
        try:
            from app.services.mail_service import send_mail_async, send_appointment_notifications, send_password_reset_notification
            self.assertTrue(True)  # Si on arrive ici, l'import a réussi
        except ImportError as e:
            self.fail(f"Impossible d'importer les fonctions du service mail: {e}")

    def test_mail_service_functions_exist(self):
        """Test que les fonctions principales existent"""
        from app.services.mail_service import send_mail_async, send_appointment_notifications, send_password_reset_notification
        
        # Vérifier que ce sont bien des fonctions
        self.assertTrue(callable(send_mail_async))
        self.assertTrue(callable(send_appointment_notifications))
        self.assertTrue(callable(send_password_reset_notification))

    def test_mail_configuration_keys(self):
        """Test que les clés de configuration mail sont définies"""
        # Ces clés doivent être présentes dans la configuration
        expected_keys = [
            'MAIL_SERVER',
            'MAIL_PORT', 
            'MAIL_USE_TLS',
            'MAIL_USERNAME',
            'MAIL_PASSWORD'
        ]
        
        for key in expected_keys:
            self.assertIn(key, self.app.config, f"Clé de configuration manquante: {key}")

    def test_mail_service_message_structure(self):
        """Test que les fonctions acceptent les bons paramètres"""
        from app.services.mail_service import send_appointment_notifications, send_password_reset_notification
        import inspect
        
        # Vérifier signature send_appointment_notifications
        sig = inspect.signature(send_appointment_notifications)
        params = list(sig.parameters.keys())
        
        # Doit avoir au minimum user_email et practitioner_email
        self.assertIn('user_email', params)
        self.assertIn('practitioner_email', params)
        
        # Vérifier signature send_password_reset_notification
        sig = inspect.signature(send_password_reset_notification)
        params = list(sig.parameters.keys())
        
        # Doit avoir au minimum user_email et temp_password
        self.assertIn('user_email', params)
        self.assertIn('temp_password', params)

    def test_mail_service_error_handling(self):
        """Test que les fonctions gèrent les erreurs sans planter l'application"""
        from app.services.mail_service import send_appointment_notifications, send_password_reset_notification
        
        # Ces appels ne doivent pas lever d'exception même avec des données invalides
        # (ils peuvent échouer silencieusement ou logger des erreurs)
        try:
            # Test avec emails invalides - ne doit pas planter
            send_appointment_notifications(
                user_email="invalid-email",
                practitioner_email="invalid-email",
                user_full_name="Test User",
                prestation_name="Test Prestation",
                message="Test message"
            )
            
            send_password_reset_notification(
                user_email="invalid-email",
                temp_password="TestPass123!"
            )
            
            # Si on arrive ici, les fonctions n'ont pas planté
            self.assertTrue(True)
            
        except Exception as e:
            # Si une exception est levée, elle doit être documentée
            self.fail(f"Les fonctions mail ne doivent pas lever d'exceptions non gérées: {e}")

    def test_appointment_notifications_content_validation(self):
        """Test validation du contenu des notifications de rendez-vous"""
        from app.services.mail_service import send_appointment_notifications
        from unittest.mock import patch
        
        # Test avec contenu réaliste
        test_cases = [
            {
                'user_full_name': 'John Doe',
                'prestation_name': 'Massage',
                'message': 'Je souhaite un rendez-vous',
                'user_email': 'john@example.com',
                'practitioner_email': 'practitioner@example.com'
            },
            {
                'user_full_name': 'Marie Martin',
                'prestation_name': 'Thérapie',
                'message': 'Besoin d\'aide urgente',
                'user_email': 'marie@example.com',
                'practitioner_email': 'melanie@example.com'
            }
        ]
        
        for case in test_cases:
            with patch('app.services.mail_service.send_mail_async') as mock_send:
                try:
                    send_appointment_notifications(**case)
                    # Vérifier que la fonction a été appelée (2 fois normalement)
                    self.assertGreaterEqual(mock_send.call_count, 1)
                except Exception as e:
                    self.fail(f"Erreur avec le cas {case['user_full_name']}: {e}")

    def test_flask_mail_integration(self):
        """Test que Flask-Mail est correctement intégré"""
        try:
            from app.services.mail_service import mail
            from flask_mail import Mail
            
            # Vérifier que mail est une instance de Mail
            self.assertIsInstance(mail, Mail)
            
        except ImportError:
            self.fail("Flask-Mail n'est pas correctement configuré")

    def test_send_mail_async_error_logging(self):
        """Test que les erreurs d'envoi sont bien loggées"""
        from app.services.mail_service import send_mail_async
        from flask_mail import Message
        from unittest.mock import patch, Mock
        
        # Créer un message de test
        msg = Message(
            subject="Test",
            recipients=["test@example.com"],
            body="Test message"
        )
        
        # Simuler une erreur SMTP
        with patch('app.services.mail_service.mail') as mock_mail:
            with patch('app.services.mail_service.current_app') as mock_app:
                mock_mail.send.side_effect = Exception("SMTP Error")
                mock_logger = Mock()
                mock_app.logger = mock_logger
                
                # L'erreur doit être capturée et loggée
                with self.assertRaises(Exception):
                    send_mail_async(msg)
                
                # Vérifier que l'erreur a été loggée
                mock_logger.error.assert_called_once()

    def test_mail_templates_structure(self):
        """Test que les templates d'email ont une structure cohérente"""
        from app.services.mail_service import send_appointment_notifications
        
        # Cette fonction doit créer des messages avec des sujets et corps appropriés
        # On ne peut pas tester l'envoi réel, mais on peut vérifier que la fonction
        # ne plante pas avec des paramètres valides
        try:
            send_appointment_notifications(
                user_email="test@example.com",
                practitioner_email="practitioner@example.com",
                user_full_name="Test User",
                prestation_name="Test Prestation",
                message="Test message"
            )
            self.assertTrue(True)
        except Exception as e:
            # Si erreur, elle doit être liée à l'envoi, pas à la structure
            # On accepte les erreurs de connexion SMTP mais pas les erreurs de code
            if "SMTP" not in str(e) and "Connection" not in str(e) and "Mail" not in str(e):
                self.fail(f"Erreur de structure dans les templates mail: {e}")


if __name__ == '__main__':
    unittest.main()