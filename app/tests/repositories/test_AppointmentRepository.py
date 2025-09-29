import unittest
from sqlalchemy.exc import SQLAlchemyError
from app.tests.base_test import BaseTest
from app.models.appointment import Appointment
from app.models.user import User
from app.models.prestation import Prestation
from app.persistence.AppointmentRepository import AppointmentRepository


class TestAppointmentRepository(BaseTest):
    def setUp(self):
        super().setUp()
        self.appointment_repo = AppointmentRepository()
        # Forcer l'utilisation de l'instance DB de test
        self.appointment_repo.db = self.db
        
        # Créer des données de test
        self.user = User(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="Password123!",
            address=None,
            phone_number=None
        )
        self.db.session.add(self.user)
        
        self.prestation = Prestation(name="Massage")
        self.db.session.add(self.prestation)
        
        self.db.session.commit()

    def test_create_appointment_success(self):
        """Test création rendez-vous réussie"""
        appointment = self.appointment_repo.create_appointment(
            message="Je souhaite prendre rendez-vous",
            user=self.user,
            prestation=self.prestation
        )
        
        self.assertIsNotNone(appointment.id)
        self.assertEqual(appointment.message, "Je souhaite prendre rendez-vous")
        self.assertEqual(appointment.user.id, self.user.id)
        self.assertEqual(appointment.prestation.id, self.prestation.id)

    def test_create_appointment_no_prestation(self):
        """Test création rendez-vous sans prestation"""
        with self.assertRaises(ValueError) as context:
            self.appointment_repo.create_appointment(
                message="Je souhaite prendre rendez-vous",
                user=self.user,
                prestation=None
            )
        
        self.assertIn("La prestation spécifiée n'existe pas", str(context.exception))

    def test_create_appointment_invalid_message(self):
        """Test création rendez-vous avec message invalide"""
        with self.assertRaises(ValueError):
            self.appointment_repo.create_appointment(
                message="",  # Message vide
                user=self.user,
                prestation=self.prestation
            )

    def test_get_by_user_id(self):
        """Test récupération rendez-vous par user_id"""
        # Créer rendez-vous
        created_appointment = self.appointment_repo.create_appointment(
            message="Rendez-vous urgent",
            user=self.user,
            prestation=self.prestation
        )
        
        # Récupérer par user_id
        found_appointment = self.appointment_repo.get_by_user_id(self.user.id)
        
        self.assertIsNotNone(found_appointment)
        self.assertEqual(found_appointment.id, created_appointment.id)

    def test_get_by_user_id_not_found(self):
        """Test récupération rendez-vous par user_id inexistant"""
        appointment = self.appointment_repo.get_by_user_id("nonexistent-id")
        self.assertIsNone(appointment)

    def test_get_by_prestation_id(self):
        """Test récupération rendez-vous par prestation_id"""
        # Créer rendez-vous
        created_appointment = self.appointment_repo.create_appointment(
            message="Première consultation",
            user=self.user,
            prestation=self.prestation
        )
        
        # Récupérer par prestation_id
        appointments = self.appointment_repo.get_by_prestation_id(self.prestation.id)
        
        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0].id, created_appointment.id)

    def test_get_by_prestation_id_multiple_appointments(self):
        """Test récupération multiple rendez-vous pour même prestation"""
        # Créer second utilisateur
        user2 = User(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="Password123!",
            address=None,
            phone_number=None
        )
        self.db.session.add(user2)
        self.db.session.commit()
        
        # Créer deux rendez-vous pour même prestation
        appointment1 = self.appointment_repo.create_appointment(
            message="Premier rendez-vous",
            user=self.user,
            prestation=self.prestation
        )
        
        appointment2 = self.appointment_repo.create_appointment(
            message="Deuxième rendez-vous",
            user=user2,
            prestation=self.prestation
        )
        
        # Récupérer tous les rendez-vous
        appointments = self.appointment_repo.get_by_prestation_id(self.prestation.id)
        
        self.assertEqual(len(appointments), 2)
        appointment_ids = [a.id for a in appointments]
        self.assertIn(appointment1.id, appointment_ids)
        self.assertIn(appointment2.id, appointment_ids)

    def test_get_by_user_and_prestation(self):
        """Test récupération rendez-vous par utilisateur et prestation"""
        # Créer rendez-vous
        created_appointment = self.appointment_repo.create_appointment(
            message="Consultation spécialisée",
            user=self.user,
            prestation=self.prestation
        )
        
        # Récupérer par user + prestation
        found_appointment = self.appointment_repo.get_by_user_and_prestation(
            self.user.id, 
            self.prestation.id
        )
        
        self.assertIsNotNone(found_appointment)
        self.assertEqual(found_appointment.id, created_appointment.id)

    def test_get_by_user_and_prestation_not_found(self):
        """Test récupération rendez-vous inexistant par user + prestation"""
        appointment = self.appointment_repo.get_by_user_and_prestation(
            "nonexistent-user", 
            "nonexistent-prestation"
        )
        self.assertIsNone(appointment)

    def test_multiple_appointments_same_user_different_prestations(self):
        """Test utilisateur avec plusieurs rendez-vous pour différentes prestations"""
        # Créer seconde prestation
        prestation2 = Prestation(name="Thérapie")
        self.db.session.add(prestation2)
        self.db.session.commit()
        
        # Créer deux rendez-vous pour même utilisateur
        appointment1 = self.appointment_repo.create_appointment(
            message="Massage relaxant",
            user=self.user,
            prestation=self.prestation
        )
        
        appointment2 = self.appointment_repo.create_appointment(
            message="Séance de thérapie",
            user=self.user,
            prestation=prestation2
        )
        
        # Vérifier que les deux rendez-vous existent
        found_appointment1 = self.appointment_repo.get_by_user_and_prestation(
            self.user.id, self.prestation.id
        )
        found_appointment2 = self.appointment_repo.get_by_user_and_prestation(
            self.user.id, prestation2.id
        )
        
        self.assertIsNotNone(found_appointment1)
        self.assertIsNotNone(found_appointment2)
        self.assertEqual(found_appointment1.id, appointment1.id)
        self.assertEqual(found_appointment2.id, appointment2.id)

    def test_inheritance_from_base_repository(self):
        """Test que AppointmentRepository hérite bien de BaseRepository"""
        # Test méthodes héritées avec create
        appointment = self.appointment_repo.create(
            message="Test appointment",
            user=self.user,
            prestation=self.prestation
        )
        self.assertIsNotNone(appointment.id)
        
        # Test get_by_id (méthode héritée)
        found_appointment = self.appointment_repo.get_by_id(appointment.id)
        self.assertEqual(found_appointment.id, appointment.id)
        
        # Test get_all (méthode héritée)
        all_appointments = self.appointment_repo.get_all()
        self.assertIn(appointment, all_appointments)

    def test_model_class_consistency(self):
        """Test que model_class est bien configuré"""
        self.assertEqual(self.appointment_repo.model_class, Appointment)


if __name__ == "__main__":
    unittest.main()