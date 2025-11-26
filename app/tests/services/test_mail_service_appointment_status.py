#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
from app.tests.base_test import BaseTest
from app.services.mail_service import send_appointment_status_notification
from flask_mail import Message


class TestMailServiceAppointmentStatus(BaseTest):
    """Tests unitaires pour les notifications de statut de rendez-vous"""
    
    def setUp(self):
        super().setUp()

    @patch('app.services.mail_service.send_mail_async')
    def test_send_appointment_status_notification_confirmed(self, mock_send):
        """Test envoi notification pour statut confirmé"""
        context = {
            'user_full_name': 'John Doe',
            'prestation_name': 'Massage Relaxant',
            'message': 'Je souhaite un rendez-vous',
            'status': 'CONFIRMED'
        }
        
        send_appointment_status_notification(
            user_email='john@example.com',
            **context
        )
        
        # Vérifier que send_mail_async a été appelé
        mock_send.assert_called_once()
        
        # Récupérer l'objet Message passé à send_mail_async
        sent_message = mock_send.call_args[0][0]
        
        self.assertIsInstance(sent_message, Message)
        self.assertIn('john@example.com', sent_message.recipients)
        self.assertIn('confirmé', sent_message.subject)
        self.assertIn('John Doe', sent_message.body)
        self.assertIn('Massage Relaxant', sent_message.body)
        self.assertIn('Je souhaite un rendez-vous', sent_message.body)

    @patch('app.services.mail_service.send_mail_async')
    def test_send_appointment_status_notification_cancelled(self, mock_send):
        """Test envoi notification pour statut annulé"""
        context = {
            'user_full_name': 'Jane Smith',
            'prestation_name': 'Consultation TCC',
            'message': 'Besoin d\'aide',
            'status': 'CANCELLED'
        }
        
        send_appointment_status_notification(
            user_email='jane@example.com',
            **context
        )
        
        mock_send.assert_called_once()
        sent_message = mock_send.call_args[0][0]
        
        self.assertIsInstance(sent_message, Message)
        self.assertIn('jane@example.com', sent_message.recipients)
        self.assertIn('annulé', sent_message.subject)
        self.assertIn('Jane Smith', sent_message.body)
        self.assertIn('Consultation TCC', sent_message.body)

    @patch('app.services.mail_service.send_mail_async')
    def test_send_appointment_status_notification_completed_no_email(self, mock_send):
        """Test qu'aucun email n'est envoyé pour le statut completed"""
        context = {
            'user_full_name': 'Bob Johnson',
            'prestation_name': 'Séance EFT',
            'message': 'Première séance',
            'status': 'completed'
        }
        
        send_appointment_status_notification(
            user_email='bob@example.com',
            **context
        )
        
        # Aucun email ne devrait être envoyé pour le statut completed
        mock_send.assert_not_called()

    @patch('app.services.mail_service.send_mail_async')
    def test_send_appointment_status_notification_pending_no_email(self, mock_send):
        """Test qu'aucun email n'est envoyé pour le statut pending"""
        context = {
            'user_full_name': 'Alice Brown',
            'prestation_name': 'Thérapie DTMA',
            'message': 'Rendez-vous urgent',
            'status': 'pending'
        }
        
        send_appointment_status_notification(
            user_email='alice@example.com',
            **context
        )
        
        # Aucun email ne devrait être envoyé pour le statut pending
        mock_send.assert_not_called()

    def test_send_appointment_status_notification_missing_context(self):
        """Test avec contexte manquant"""
        incomplete_contexts = [
            {
                'prestation_name': 'Test',
                'message': 'Test',
                'status': 'CONFIRMED'
                # Manque user_full_name
            },
            {
                'user_full_name': 'Test User',
                'message': 'Test',
                'status': 'CONFIRMED'
                # Manque prestation_name
            },
            {
                'user_full_name': 'Test User',
                'prestation_name': 'Test',
                'status': 'CONFIRMED'
                # Manque message
            },
            {
                'user_full_name': 'Test User',
                'prestation_name': 'Test',
                'message': 'Test'
                # Manque status
            }
        ]
        
        for context in incomplete_contexts:
            with self.assertRaises(ValueError) as cm:
                send_appointment_status_notification(
                    user_email='test@example.com',
                    **context
                )
            
            self.assertIn('manquantes', str(cm.exception))

    @patch('app.services.mail_service.send_mail_async')
    def test_send_appointment_status_notification_confirmed_content(self, mock_send):
        """Test contenu détaillé de l'email de confirmation"""
        context = {
            'user_full_name': 'Marie Dubois',
            'prestation_name': 'Hypnose Thérapeutique',
            'message': 'Problème de stress au travail',
            'status': 'CONFIRMED'
        }
        
        send_appointment_status_notification(
            user_email='marie@example.com',
            **context
        )
        
        sent_message = mock_send.call_args[0][0]
        
        # Vérifier le sujet
        self.assertIn('Hypnose Thérapeutique', sent_message.subject)
        self.assertIn('confirmé', sent_message.subject)
        
        # Vérifier le contenu du corps
        body = sent_message.body
        self.assertIn('Marie Dubois', body)
        self.assertIn('Hypnose Thérapeutique', body)
        self.assertIn('Problème de stress au travail', body)
        self.assertIn('confirmer', body)
        self.assertIn('Mélanie Laborda', body)

    @patch('app.services.mail_service.send_mail_async')
    def test_send_appointment_status_notification_cancelled_content(self, mock_send):
        """Test contenu détaillé de l'email d'annulation"""
        context = {
            'user_full_name': 'Pierre Martin',
            'prestation_name': 'Séance PNL',
            'message': 'Améliorer ma confiance en moi',
            'status': 'CANCELLED'
        }
        
        send_appointment_status_notification(
            user_email='pierre@example.com',
            **context
        )
        
        sent_message = mock_send.call_args[0][0]
        
        # Vérifier le sujet
        self.assertIn('Séance PNL', sent_message.subject)
        self.assertIn('annulé', sent_message.subject)
        
        # Vérifier le contenu du corps
        body = sent_message.body
        self.assertIn('Pierre Martin', body)
        self.assertIn('Séance PNL', body)
        self.assertIn('annulé', body)
        self.assertIn('replanifier', body)
        self.assertIn('Mélanie Laborda', body)

    @patch('app.services.mail_service.send_mail_async')
    def test_send_appointment_status_notification_sender_config(self, mock_send):
        """Test que l'expéditeur est correctement configuré"""
        context = {
            'user_full_name': 'Test User',
            'prestation_name': 'Test Prestation',
            'message': 'Test message',
            'status': 'CONFIRMED'
        }
        
        send_appointment_status_notification(
            user_email='test@example.com',
            **context
        )
        
        sent_message = mock_send.call_args[0][0]
        
        # Vérifier que l'expéditeur est configuré depuis la config
        expected_sender = self.app.config.get('MAIL_DEFAULT_SENDER')
        self.assertEqual(sent_message.sender, expected_sender)

    @patch('app.services.mail_service.send_mail_async')
    def test_send_appointment_status_notification_special_characters(self, mock_send):
        """Test avec caractères spéciaux dans le contexte"""
        context = {
            'user_full_name': 'José María',
            'prestation_name': 'Thérapie émotionnelle',
            'message': 'J\'ai des difficultés à gérer mes émotions',
            'status': 'CONFIRMED'
        }
        
        send_appointment_status_notification(
            user_email='jose@example.com',
            **context
        )
        
        mock_send.assert_called_once()
        sent_message = mock_send.call_args[0][0]
        
        # Vérifier que les caractères spéciaux sont correctement gérés
        self.assertIn('José María', sent_message.body)
        self.assertIn('émotionnelle', sent_message.body)
        self.assertIn('gérer mes émotions', sent_message.body)


if __name__ == '__main__':
    unittest.main()