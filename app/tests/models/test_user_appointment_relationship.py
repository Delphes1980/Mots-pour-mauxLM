import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prestation import Prestation
from app.models.review import Review

class TestUserAppointmentRelations(BaseTest):
    def setUp(self):
        super().setUp()
        self.user = User(first_name="John", last_name="Doe",
                         email="john@example.com", 
                         password="Password123!", is_admin=False)
        self.user2 = User(first_name="Jane", last_name="Smith",
                         email="jane@example.com", 
                         password="Password123!", is_admin=False)
        self.prestation = Prestation(name="Massage thérapeutique")
        self.save_to_db(self.user, self.user2, self.prestation)

    def test_user_can_create_appointment(self):
        # Un utilisateur peut créer un rendez-vous
        appointment = Appointment(subject="Massage suédois", 
                                message="Je souhaite un rendez-vous", 
                                user=self.user, prestation=self.prestation)
        self.assertEqual(appointment.user, self.user)
        self.assertEqual(appointment._user_id, self.user.id)

    def test_user_multiple_appointments(self):
        # Un utilisateur peut avoir plusieurs rendez-vous
        appointment1 = Appointment(subject="Massage thérapeutique", 
                                 message="Première séance", user=self.user, prestation=self.prestation)
        appointment2 = Appointment(subject="Réflexologie", 
                                 message="Deuxième séance", user=self.user, prestation=self.prestation)
        
        self.assertEqual(appointment1.user, self.user)
        self.assertEqual(appointment2.user, self.user)
        self.assertNotEqual(appointment1.id, appointment2.id)

    def test_appointment_belongs_to_one_user(self):
        # Un rendez-vous appartient à un seul utilisateur
        appointment = Appointment(subject="Aromathérapie", 
                                message="Séance relaxante", user=self.user, prestation=self.prestation)
        
        # Changer d'utilisateur (cas de transfert de RDV)
        appointment.user = self.user2
        self.assertEqual(appointment.user, self.user2)
        self.assertEqual(appointment._user_id, self.user2.id)

    def test_different_users_different_appointments(self):
        # Différents utilisateurs peuvent prendre des rendez-vous
        appointment1 = Appointment(subject="Massage californien", 
                                 message="Détente totale", user=self.user, prestation=self.prestation)
        appointment2 = Appointment(subject="Massage deep tissue", 
                                 message="Soulager tensions", user=self.user2, prestation=self.prestation)
        
        self.assertEqual(appointment1.user, self.user)
        self.assertEqual(appointment2.user, self.user2)
        self.assertNotEqual(appointment1._user_id, appointment2._user_id)

    def test_user_appointment_services_variety(self):
        # Un utilisateur peut réserver différents services
        services = [
            ("Massage suédois", "Relaxation"),
            ("Réflexologie plantaire", "Bien-être des pieds"),
            ("Aromathérapie", "Huiles essentielles")
        ]
        
        appointments = []
        for subject, message in services:
            appointment = Appointment(subject=subject, message=message, user=self.user, prestation=self.prestation)
            appointments.append(appointment)
        
        # Vérifier que tous appartiennent au même utilisateur
        for appointment in appointments:
            self.assertEqual(appointment.user, self.user)
        
        # Vérifier l'unicité des rendez-vous
        ids = [apt.id for apt in appointments]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
