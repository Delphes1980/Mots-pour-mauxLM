import unittest
from unittest.mock import patch, MagicMock
from app.tests.base_test import BaseTest
from app.services.AppointmentService import AppointmentService
from app.services.UserService import UserService
from app.services.PrestationService import PrestationService


class TestAppointmentService(BaseTest):
    
    def setUp(self):
        super().setUp()
        self.appointment_service = AppointmentService()
        self.user_service = UserService()
        self.prestation_service = PrestationService()
        
        # Créer des données de test
        self.test_user = self.user_service.create_user(
            first_name="John",
            last_name="Doe", 
            email="john@example.com",
            password="Password123!"
        )
        
        self.test_prestation = self.prestation_service.create_prestation(name="Thérapie individuelle")
    
    # Tests pour create_appointment()
    @patch('app.services.AppointmentService.send_appointment_notifications')
    @patch('flask.current_app')
    def test_create_appointment_success(self, mock_current_app, mock_send_notifications):
        """Test création de rendez-vous réussie"""
        mock_current_app.config.get.return_value = "practitioner@example.com"
        
        appointment = self.appointment_service.create_appointment(
            message="Je souhaite prendre rendez-vous",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.message, "Je souhaite prendre rendez-vous")
        self.assertEqual(appointment.user_id, self.test_user.id)
        self.assertEqual(appointment.prestation_id, self.test_prestation.id)
        
        # Vérifier que l'email a été envoyé
        mock_send_notifications.assert_called_once()
    
    def test_create_appointment_no_practitioner_email(self):
        """Test création sans email praticien configuré"""
        from flask import current_app
        
        # Temporairement désactiver l'email praticien
        with patch.object(current_app.config, 'get') as mock_config:
            mock_config.side_effect = lambda key: None if key == "MAIL_RECIPIENT_PRACTITIONER" else current_app.config.get(key)
            
            appointment = self.appointment_service.create_appointment(
                message="Test message",
                user_id=self.test_user.id,
                prestation_id=self.test_prestation.id
            )
            
            self.assertIsNotNone(appointment)
    
    def test_create_appointment_missing_message(self):
        """Test création sans message"""
        with self.assertRaises(ValueError):
            self.appointment_service.create_appointment(
                user_id=self.test_user.id,
                prestation_id=self.test_prestation.id
            )
    
    def test_create_appointment_empty_message(self):
        """Test création avec message vide"""
        with self.assertRaises(ValueError):
            self.appointment_service.create_appointment(
                message="",
                user_id=self.test_user.id,
                prestation_id=self.test_prestation.id
            )
    
    def test_create_appointment_message_too_long(self):
        """Test création avec message trop long"""
        long_message = "A" * 501  # Plus de 500 caractères
        with self.assertRaises(ValueError):
            self.appointment_service.create_appointment(
                message=long_message,
                user_id=self.test_user.id,
                prestation_id=self.test_prestation.id
            )
    
    def test_create_appointment_invalid_user_id(self):
        """Test création avec ID utilisateur invalide"""
        with self.assertRaises(ValueError) as context:
            self.appointment_service.create_appointment(
                message="Test message",
                user_id="invalid-id",
                prestation_id=self.test_prestation.id
            )
        self.assertIn("user_id", str(context.exception))
    
    def test_create_appointment_user_not_found(self):
        """Test création avec utilisateur inexistant"""
        from uuid import uuid4
        fake_user_id = str(uuid4())
        
        with self.assertRaises(ValueError) as context:
            self.appointment_service.create_appointment(
                message="Test message",
                user_id=fake_user_id,
                prestation_id=self.test_prestation.id
            )
        self.assertEqual(str(context.exception), "Utilisateur introuvable")
    
    def test_create_appointment_invalid_prestation_id(self):
        """Test création avec ID prestation invalide"""
        with self.assertRaises(ValueError) as context:
            self.appointment_service.create_appointment(
                message="Test message",
                user_id=self.test_user.id,
                prestation_id="invalid-id"
            )
        self.assertIn("prestation_id", str(context.exception))
    
    def test_create_appointment_prestation_not_found(self):
        """Test création avec prestation inexistante"""
        from uuid import uuid4
        fake_prestation_id = str(uuid4())
        
        with self.assertRaises(ValueError) as context:
            self.appointment_service.create_appointment(
                message="Test message",
                user_id=self.test_user.id,
                prestation_id=fake_prestation_id
            )
        self.assertEqual(str(context.exception), "Prestation introuvable")
    
    # Tests pour get_appointment_by_id()
    @patch('app.services.AppointmentService.send_appointment_notifications')
    @patch('flask.current_app')
    def test_get_appointment_by_id_success(self, mock_current_app, mock_send_notifications):
        """Test récupération de rendez-vous par ID"""
        mock_current_app.config.get.return_value = "practitioner@example.com"
        
        # Créer un rendez-vous
        appointment = self.appointment_service.create_appointment(
            message="Test message",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        # Récupérer le rendez-vous
        retrieved_appointment = self.appointment_service.get_appointment_by_id(appointment.id)
        
        self.assertEqual(retrieved_appointment.id, appointment.id)
        self.assertEqual(retrieved_appointment.message, "Test message")
    
    def test_get_appointment_by_id_invalid_id(self):
        """Test récupération avec ID invalide"""
        with self.assertRaises(ValueError) as context:
            self.appointment_service.get_appointment_by_id("invalid-id")
        self.assertIn("appointment_id", str(context.exception))
    
    def test_get_appointment_by_id_not_found(self):
        """Test récupération avec ID inexistant"""
        from uuid import uuid4
        fake_id = str(uuid4())
        
        with self.assertRaises(ValueError) as context:
            self.appointment_service.get_appointment_by_id(fake_id)
        self.assertEqual(str(context.exception), "Rendez-vous introuvable")
    
    # Tests pour get_all_appointments()
    @patch('app.services.AppointmentService.send_appointment_notifications')
    @patch('flask.current_app')
    def test_get_all_appointments(self, mock_current_app, mock_send_notifications):
        """Test récupération de tous les rendez-vous"""
        mock_current_app.config.get.return_value = "practitioner@example.com"
        
        # Créer plusieurs rendez-vous
        appointment1 = self.appointment_service.create_appointment(
            message="Premier rendez-vous",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        appointment2 = self.appointment_service.create_appointment(
            message="Deuxième rendez-vous",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        all_appointments = self.appointment_service.get_all_appointments()
        
        self.assertEqual(len(all_appointments), 2)
        appointment_ids = [apt.id for apt in all_appointments]
        self.assertIn(appointment1.id, appointment_ids)
        self.assertIn(appointment2.id, appointment_ids)
    
    # Tests pour get_appointment_by_prestation()
    @patch('app.services.AppointmentService.send_appointment_notifications')
    @patch('flask.current_app')
    def test_get_appointment_by_prestation(self, mock_current_app, mock_send_notifications):
        """Test récupération par prestation"""
        mock_current_app.config.get.return_value = "practitioner@example.com"
        
        # Créer un autre prestation
        prestation2 = self.prestation_service.create_prestation(name="Thérapie de couple")
        
        # Créer des rendez-vous pour différentes prestations
        appointment1 = self.appointment_service.create_appointment(
            message="Rendez-vous thérapie individuelle",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        appointment2 = self.appointment_service.create_appointment(
            message="Rendez-vous thérapie de couple",
            user_id=self.test_user.id,
            prestation_id=prestation2.id
        )
        
        # Récupérer les rendez-vous par prestation
        appointments_prestation1 = self.appointment_service.get_appointment_by_prestation(self.test_prestation.id)
        appointments_prestation2 = self.appointment_service.get_appointment_by_prestation(prestation2.id)
        
        self.assertEqual(len(appointments_prestation1), 1)
        self.assertEqual(len(appointments_prestation2), 1)
        self.assertEqual(appointments_prestation1[0].id, appointment1.id)
        self.assertEqual(appointments_prestation2[0].id, appointment2.id)
    
    def test_get_appointment_by_prestation_invalid_id(self):
        """Test récupération par prestation avec ID invalide"""
        with self.assertRaises(ValueError) as context:
            self.appointment_service.get_appointment_by_prestation("invalid-id")
        self.assertIn("prestation_id", str(context.exception))
    
    # Tests pour get_appointment_by_user()
    @patch('app.services.AppointmentService.send_appointment_notifications')
    @patch('flask.current_app')
    def test_get_appointment_by_user(self, mock_current_app, mock_send_notifications):
        """Test récupération par utilisateur"""
        mock_current_app.config.get.return_value = "practitioner@example.com"
        
        # Créer un autre utilisateur
        user2 = self.user_service.create_user(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="Password123!"
        )
        
        # Créer des rendez-vous pour différents utilisateurs
        appointment1 = self.appointment_service.create_appointment(
            message="Rendez-vous John",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        appointment2 = self.appointment_service.create_appointment(
            message="Rendez-vous Jane",
            user_id=user2.id,
            prestation_id=self.test_prestation.id
        )
        
        # Récupérer les rendez-vous par utilisateur
        appointments_user1 = self.appointment_service.get_appointment_by_user(self.test_user.id)
        appointments_user2 = self.appointment_service.get_appointment_by_user(user2.id)
        
        self.assertEqual(len(appointments_user1), 1)
        self.assertEqual(len(appointments_user2), 1)
        self.assertEqual(appointments_user1[0].id, appointment1.id)
        self.assertEqual(appointments_user2[0].id, appointment2.id)
    
    def test_get_appointment_by_user_invalid_id(self):
        """Test récupération par utilisateur avec ID invalide"""
        with self.assertRaises(ValueError) as context:
            self.appointment_service.get_appointment_by_user("invalid-id")
        self.assertIn("user_id", str(context.exception))
    
    # Tests pour get_appointment_by_user_and_prestation()
    @patch('app.services.AppointmentService.send_appointment_notifications')
    @patch('flask.current_app')
    def test_get_appointment_by_user_and_prestation_success(self, mock_current_app, mock_send_notifications):
        """Test récupération par utilisateur et prestation"""
        mock_current_app.config.get.return_value = "practitioner@example.com"
        
        # Créer un rendez-vous
        appointment = self.appointment_service.create_appointment(
            message="Test message",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        # Récupérer le rendez-vous
        appointments = self.appointment_service.get_appointment_by_user_and_prestation(
            self.test_user.id, 
            self.test_prestation.id
        )
        
        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0].id, appointment.id)
    
    def test_get_appointment_by_user_and_prestation_invalid_user_id(self):
        """Test récupération avec ID utilisateur invalide"""
        with self.assertRaises(ValueError) as context:
            self.appointment_service.get_appointment_by_user_and_prestation(
                "invalid-id", 
                self.test_prestation.id
            )
        self.assertIn("user_id", str(context.exception))
    
    def test_get_appointment_by_user_and_prestation_invalid_prestation_id(self):
        """Test récupération avec ID prestation invalide"""
        with self.assertRaises(ValueError) as context:
            self.appointment_service.get_appointment_by_user_and_prestation(
                self.test_user.id, 
                "invalid-id"
            )
        self.assertIn("prestation_id", str(context.exception))
    
    def test_get_appointment_by_user_and_prestation_user_not_found(self):
        """Test récupération avec utilisateur inexistant"""
        from uuid import uuid4
        fake_user_id = str(uuid4())
        
        with self.assertRaises(ValueError) as context:
            self.appointment_service.get_appointment_by_user_and_prestation(
                fake_user_id, 
                self.test_prestation.id
            )
        self.assertEqual(str(context.exception), "Utilisateur non trouvé")
    
    def test_get_appointment_by_user_and_prestation_prestation_not_found(self):
        """Test récupération avec prestation inexistante"""
        from uuid import uuid4
        fake_prestation_id = str(uuid4())
        
        with self.assertRaises(ValueError) as context:
            self.appointment_service.get_appointment_by_user_and_prestation(
                self.test_user.id, 
                fake_prestation_id
            )
        self.assertEqual(str(context.exception), "Prestation non trouvée")
    
    def test_get_appointment_by_user_and_prestation_not_found(self):
        """Test récupération sans rendez-vous existant"""
        # Créer un autre utilisateur sans rendez-vous
        user2 = self.user_service.create_user(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="Password123!"
        )
        
        with self.assertRaises(ValueError) as context:
            self.appointment_service.get_appointment_by_user_and_prestation(
                user2.id, 
                self.test_prestation.id
            )
        self.assertEqual(str(context.exception), "Rendez-vous non trouvés pour cet utilisateur et cette prestation")
    
    # Tests d'intégration pour l'envoi d'email
    def test_email_integration_success(self):
        """Test d'intégration pour l'envoi d'email avec vraie config"""
        from flask import current_app
        
        with patch('app.services.mail_service.send_mail_async') as mock_send_mail:
            appointment = self.appointment_service.create_appointment(
                message="Je souhaite prendre rendez-vous pour discuter de mes problèmes",
                user_id=self.test_user.id,
                prestation_id=self.test_prestation.id
            )
            
            # Utiliser la vraie configuration de test
            expected_practitioner = current_app.config.get("MAIL_RECIPIENT_PRACTITIONER")
            
            # Vérifier que send_mail_async a été appelé 2 fois (praticien + utilisateur)
            self.assertEqual(mock_send_mail.call_count, 2)
            
            # Vérifier le contenu des emails
            calls = mock_send_mail.call_args_list
            
            # Premier appel (email praticien)
            practitioner_message = calls[0][0][0]
            self.assertIn("Nouvelle demande de rendez-vous", practitioner_message.subject)
            self.assertIn("John Doe", practitioner_message.body)
            self.assertIn("Thérapie individuelle", practitioner_message.body)
            self.assertEqual(practitioner_message.recipients, [expected_practitioner])
            
            # Deuxième appel (email utilisateur)
            user_message = calls[1][0][0]
            self.assertIn("Confirmation", user_message.subject)
            self.assertIn("John", user_message.body)
            self.assertIn("Mélanie Laborda", user_message.body)
            self.assertEqual(user_message.recipients, ["john@example.com"])
    
    def test_email_configuration_exists(self):
        """Vérifier que la configuration email est présente et valide"""
        from flask import current_app
        
        practitioner_email = current_app.config.get("MAIL_RECIPIENT_PRACTITIONER")
        sender_email = current_app.config.get("MAIL_USERNAME")
        
        # Vérifier que les emails sont configurés
        self.assertIsNotNone(practitioner_email, "MAIL_RECIPIENT_PRACTITIONER doit être configuré")
        self.assertIsNotNone(sender_email, "MAIL_USERNAME doit être configuré")
        
        # Vérifier le format des emails
        self.assertIn("@", practitioner_email, "Email praticien invalide")
        self.assertIn("@", sender_email, "Email expéditeur invalide")
        
        # Vérifier que c'est bien la config de test
        self.assertTrue(current_app.config.get("TESTING"), "Doit utiliser la configuration de test")


if __name__ == '__main__':
    unittest.main()