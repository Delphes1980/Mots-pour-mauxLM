import unittest
from datetime import datetime
from app.tests.base_test import BaseTest
from app.models.appointment import Appointment
from app.models.user import User
from app.models.prestation import Prestation


class TestAppointment(BaseTest):
    def setUp(self):
        super().setUp()
        self.user = User(first_name="John", last_name="Doe",
                         email="john@example.com", address=None, phone_number=None,
                         password="Password123!", is_admin=False)
        self.user2 = User(first_name="Jane", last_name="Smith",
                         email="jane@example.com", address=None, phone_number=None,
                         password="Password123!", is_admin=False)
        self.user3 = User(first_name="Jim", last_name="Brown",
                         email="jim@example.com", address=None, phone_number=None,
                         password="Password123!", is_admin=False)
        self.prestation = Prestation(name="Massage thérapeutique")
        self.save_to_db(self.user, self.user2, self.user3, self.prestation)
        self.valid_data = {
            'subject': 'Massage therapy session',
            'message': 'I would like to book a relaxing massage session for next week.',
            'user': self.user,
            'prestation': self.prestation
        }

    def test_appointment_creation_valid(self):
        appointment = Appointment(**self.valid_data)
        self.assertEqual(appointment.subject, self.valid_data['subject'])
        self.assertEqual(appointment.message, self.valid_data['message'])
        self.assertEqual(appointment.user, self.user)

    def test_missing_required_fields(self):
        with self.assertRaises(ValueError):
            Appointment(subject=None, message="Valid message", user=self.user, prestation=self.prestation)
        with self.assertRaises(ValueError):
            Appointment(subject="Valid subject", message=None, user=self.user, prestation=self.prestation)
        with self.assertRaises(ValueError):
            Appointment(subject="Valid subject", message="Valid message", user=None, prestation=self.prestation)

    def test_invalid_subject_type_and_length(self):
        with self.assertRaises(ValueError):
            Appointment(subject='', message="Valid message", user=self.user, prestation=self.prestation)
        with self.assertRaises(TypeError):
            Appointment(subject=123, message="Valid message", user=self.user, prestation=self.prestation)
        with self.assertRaises(ValueError):
            Appointment(subject='A'*51, message="Valid message", user=self.user, prestation=self.prestation)

    def test_invalid_message_type_and_length(self):
        with self.assertRaises(ValueError):
            Appointment(subject="Valid subject", message='', user=self.user, prestation=self.prestation)
        with self.assertRaises(TypeError):
            Appointment(subject="Valid subject", message=123, user=self.user, prestation=self.prestation)
        with self.assertRaises(ValueError):
            Appointment(subject="Valid subject", message='A'*501, user=self.user, prestation=self.prestation)

    def test_subject_boundaries(self):
        # Test limites valides
        appointment1 = Appointment(subject="A", message="Valid message", user=self.user, prestation=self.prestation)
        appointment50 = Appointment(subject="A"*50, message="Valid message", user=self.user2, prestation=self.prestation)
        self.assertEqual(appointment1.subject, "A")
        self.assertEqual(appointment50.subject, "A"*50)

    def test_message_boundaries(self):
        # Test limites valides
        appointment1 = Appointment(subject="Valid subject", message="A", user=self.user, prestation=self.prestation)
        appointment500 = Appointment(subject="Valid subject", message="A"*500, user=self.user2, prestation=self.prestation)
        self.assertEqual(appointment1.message, "A")
        self.assertEqual(appointment500.message, "A"*500)

    def test_property_setters(self):
        appointment = Appointment(**self.valid_data)
        appointment.subject = "Updated subject"
        appointment.message = "Updated message content"
        self.assertEqual(appointment.subject, "Updated subject")
        self.assertEqual(appointment.message, "Updated message content")

    def test_invalid_user_type(self):
        with self.assertRaises(TypeError):
            Appointment(subject="Valid subject", message="Valid message", user="not_a_user", prestation=self.prestation)

    def test_inherited_attributes(self):
        appointment = Appointment(**self.valid_data)
        self.assertIsInstance(appointment.id, str)
        self.assertIsInstance(appointment.created_at, datetime)
        self.assertIsInstance(appointment.updated_at, datetime)

    def test_predefined_services(self):
        # Test des prestations prédéfinies du menu déroulant
        valid_services = [
            "Massage suédois",
            "Massage thérapeutique", 
            "Réflexologie plantaire",
            "Aromathérapie",
            "Massage relaxant",
            "Massage deep tissue",
            "Massage californien"
        ]
        
        for service in valid_services:
            appointment = Appointment(subject=service, message="Demande de rendez-vous", user=self.user, prestation=self.prestation)
            self.assertEqual(appointment.subject, service)

    def test_service_selection_validation(self):
        # Test que les services du menu sont correctement acceptés
        services_with_messages = [
            ("Massage suédois", "Je souhaite un massage relaxant"),
            ("Réflexologie plantaire", "Séance pour soulager le stress"),
            ("Aromathérapie", "Thérapie aux huiles essentielles")
        ]
        
        for service, message in services_with_messages:
            appointment = Appointment(subject=service, message=message, user=self.user, prestation=self.prestation)
            self.assertEqual(appointment.subject, service)
            self.assertEqual(appointment.message, message)

    def test_user_assignment(self):
        appointment = Appointment(subject="Therapy session", message="Book a session", user=self.user, prestation=self.prestation)
        self.assertEqual(appointment.user, self.user)
        self.assertEqual(appointment._user_id, self.user.id)
        
        # Test changing user
        appointment.user = self.user2
        self.assertEqual(appointment.user, self.user2)
        self.assertEqual(appointment._user_id, self.user2.id)

    def test_multiple_appointments_same_user(self):
        # Un même utilisateur peut prendre plusieurs rendez-vous
        appointment1 = Appointment(subject="Massage therapy", message="Relaxing massage", user=self.user, prestation=self.prestation)
        appointment2 = Appointment(subject="Reflexology", message="Foot reflexology session", user=self.user, prestation=self.prestation)
        appointment3 = Appointment(subject="Aromatherapy", message="Essential oils therapy", user=self.user, prestation=self.prestation)
        
        # Vérifier que tous les rendez-vous sont créés avec le même utilisateur
        self.assertEqual(appointment1.user, self.user)
        self.assertEqual(appointment2.user, self.user)
        self.assertEqual(appointment3.user, self.user)
        
        # Vérifier que les rendez-vous ont des contenus différents
        self.assertNotEqual(appointment1.subject, appointment2.subject)
        self.assertNotEqual(appointment2.subject, appointment3.subject)
        
        # Vérifier que les rendez-vous ont des IDs uniques
        self.assertNotEqual(appointment1.id, appointment2.id)
        self.assertNotEqual(appointment2.id, appointment3.id)

    def test_appointment_different_services(self):
        # Test pour différents types de prestations
        services = [
            ("Massage suédois", "Massage relaxant de 60 minutes"),
            ("Réflexologie plantaire", "Séance de réflexologie des pieds"),
            ("Aromathérapie", "Thérapie aux huiles essentielles"),
            ("Massage thérapeutique", "Massage pour soulager les tensions")
        ]
        
        appointments = []
        for subject, message in services:
            appointment = Appointment(subject=subject, message=message, user=self.user, prestation=self.prestation)
            appointments.append(appointment)
            self.assertEqual(appointment.subject, subject)
            self.assertEqual(appointment.message, message)
            self.assertEqual(appointment.user, self.user)
        
        # Vérifier que tous les rendez-vous sont uniques
        ids = [apt.id for apt in appointments]
        self.assertEqual(len(ids), len(set(ids)))  # Tous les IDs sont uniques


if __name__ == "__main__":
    unittest.main()