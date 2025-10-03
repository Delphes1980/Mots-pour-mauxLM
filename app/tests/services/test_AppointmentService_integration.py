import unittest
from app.tests.base_test import BaseTest
from app.services.AppointmentService import AppointmentService
from app.services.UserService import UserService
from app.services.PrestationService import PrestationService


class TestAppointmentServiceIntegration(BaseTest):
    """Tests d'intégration complets pour AppointmentService sans aucun mock"""
    
    def setUp(self):
        super().setUp()
        self.appointment_service = AppointmentService()
        self.user_service = UserService()
        self.prestation_service = PrestationService()
        
        # Créer des données de test réelles
        self.test_user = self.user_service.create_user(
            first_name="John",
            last_name="Doe", 
            email="john@example.com",
            password="Password123!"
        )
        
        self.test_prestation = self.prestation_service.create_prestation(name="Thérapie individuelle")
    
    def test_create_appointment_full_integration(self):
        """Test d'intégration complet création de rendez-vous"""
        # Aucun mock - test bout-en-bout complet
        appointment = self.appointment_service.create_appointment(
            message="Je souhaite prendre rendez-vous pour discuter de mes problèmes",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        # Vérifications complètes
        self.assertIsNotNone(appointment)
        self.assertIsNotNone(appointment.id)
        self.assertEqual(appointment.message, "Je souhaite prendre rendez-vous pour discuter de mes problèmes")
        self.assertEqual(appointment.user_id, self.test_user.id)
        self.assertEqual(appointment.prestation_id, self.test_prestation.id)
        
        # Vérifier que l'appointment est bien en base
        retrieved = self.appointment_service.get_appointment_by_id(appointment.id)
        self.assertEqual(retrieved.id, appointment.id)
        self.assertEqual(retrieved.message, appointment.message)
    
    def test_appointment_workflow_integration(self):
        """Test d'intégration workflow complet de gestion des rendez-vous"""
        # 1. Créer plusieurs utilisateurs et prestations
        user2 = self.user_service.create_user(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="Password123!"
        )
        
        prestation2 = self.prestation_service.create_prestation(name="Thérapie de couple")
        
        # 2. Créer plusieurs rendez-vous
        appointment1 = self.appointment_service.create_appointment(
            message="Premier rendez-vous individuel",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        appointment2 = self.appointment_service.create_appointment(
            message="Rendez-vous de couple",
            user_id=user2.id,
            prestation_id=prestation2.id
        )
        
        appointment3 = self.appointment_service.create_appointment(
            message="Deuxième rendez-vous individuel",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        # 3. Tester les différentes méthodes de récupération
        
        # Tous les rendez-vous
        all_appointments = self.appointment_service.get_all_appointments()
        self.assertEqual(len(all_appointments), 3)
        
        # Par utilisateur
        user1_appointments = self.appointment_service.get_appointment_by_user(self.test_user.id)
        user2_appointments = self.appointment_service.get_appointment_by_user(user2.id)
        self.assertEqual(len(user1_appointments), 2)
        self.assertEqual(len(user2_appointments), 1)
        
        # Par prestation
        prestation1_appointments = self.appointment_service.get_appointment_by_prestation(self.test_prestation.id)
        prestation2_appointments = self.appointment_service.get_appointment_by_prestation(prestation2.id)
        self.assertEqual(len(prestation1_appointments), 2)
        self.assertEqual(len(prestation2_appointments), 1)
        
        # Par utilisateur et prestation
        user1_prestation1 = self.appointment_service.get_appointment_by_user_and_prestation(
            self.test_user.id, self.test_prestation.id
        )
        self.assertEqual(len(user1_prestation1), 2)
        
        # Vérifier les IDs
        appointment_ids = [apt.id for apt in user1_prestation1]
        self.assertIn(appointment1.id, appointment_ids)
        self.assertIn(appointment3.id, appointment_ids)
    
    def test_appointment_data_integrity_integration(self):
        """Test d'intégration intégrité des données"""
        # Créer un rendez-vous
        appointment = self.appointment_service.create_appointment(
            message="Test intégrité des données",
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        
        # Vérifier que les relations sont correctes
        retrieved = self.appointment_service.get_appointment_by_id(appointment.id)
        
        # Vérifier les relations via les propriétés hybrides
        self.assertEqual(retrieved.user_id, self.test_user.id)
        self.assertEqual(retrieved.prestation_id, self.test_prestation.id)
        
        # Vérifier que les objets liés existent
        user = self.user_service.get_user_by_id(retrieved.user_id)
        prestation = self.prestation_service.get_prestation_by_id(retrieved.prestation_id)
        
        self.assertEqual(user.id, self.test_user.id)
        self.assertEqual(prestation.id, self.test_prestation.id)
    
    def test_appointment_validation_integration(self):
        """Test d'intégration validation complète"""
        # Test avec message trop long
        long_message = "A" * 501
        with self.assertRaises(ValueError):
            self.appointment_service.create_appointment(
                message=long_message,
                user_id=self.test_user.id,
                prestation_id=self.test_prestation.id
            )
        
        # Test avec utilisateur inexistant
        from uuid import uuid4
        fake_user_id = str(uuid4())
        with self.assertRaises(ValueError) as context:
            self.appointment_service.create_appointment(
                message="Test message",
                user_id=fake_user_id,
                prestation_id=self.test_prestation.id
            )
        self.assertEqual(str(context.exception), "Utilisateur introuvable")
        
        # Test avec prestation inexistante
        fake_prestation_id = str(uuid4())
        with self.assertRaises(ValueError) as context:
            self.appointment_service.create_appointment(
                message="Test message",
                user_id=self.test_user.id,
                prestation_id=fake_prestation_id
            )
        self.assertEqual(str(context.exception), "Prestation introuvable")
    
    def test_appointment_edge_cases_integration(self):
        """Test d'intégration cas limites"""
        # Message à la limite (500 caractères)
        limit_message = "A" * 500
        appointment = self.appointment_service.create_appointment(
            message=limit_message,
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        self.assertEqual(len(appointment.message), 500)
        
        # Message minimal (1 caractère)
        minimal_message = "A"
        appointment2 = self.appointment_service.create_appointment(
            message=minimal_message,
            user_id=self.test_user.id,
            prestation_id=self.test_prestation.id
        )
        self.assertEqual(appointment2.message, "A")
        
        # Vérifier que les deux sont bien créés
        all_appointments = self.appointment_service.get_all_appointments()
        self.assertGreaterEqual(len(all_appointments), 2)
    
    def test_multiple_appointments_same_user_prestation_integration(self):
        """Test d'intégration plusieurs rendez-vous même utilisateur/prestation"""
        # Un utilisateur peut avoir plusieurs rendez-vous pour la même prestation
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
        
        # Vérifier que les deux existent
        appointments = self.appointment_service.get_appointment_by_user_and_prestation(
            self.test_user.id, self.test_prestation.id
        )
        
        self.assertEqual(len(appointments), 2)
        messages = [apt.message for apt in appointments]
        self.assertIn("Premier rendez-vous", messages)
        self.assertIn("Deuxième rendez-vous", messages)


if __name__ == '__main__':
    unittest.main()