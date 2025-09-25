import unittest
from app.models.prestation import Prestation
from app.models.appointment import Appointment
from app.models.user import User
from app.models.review import Review


class TestPrestationAppointmentRelations(unittest.TestCase):
    def setUp(self):
        self.user = User(first_name="John", last_name="Doe",
                         email="john@example.com", 
                         password="Password123!", is_admin=False)
        self.prestation = Prestation(name="Massage suédois")
        self.prestation2 = Prestation(name="Réflexologie plantaire")

    def test_prestation_can_have_appointment(self):
        # Une prestation peut avoir un rendez-vous
        appointment = Appointment(user=self.user, subject="Rendez-vous massage", 
                                message="Je souhaite un massage", prestation=self.prestation)
        self.assertEqual(appointment.prestation, self.prestation)
        self.assertEqual(appointment._prestation_id, self.prestation.id)

    def test_prestation_multiple_appointments(self):
        # Une prestation peut avoir plusieurs rendez-vous
        appointment1 = Appointment(user=self.user, subject="Premier RDV", 
                                 message="Premier massage", prestation=self.prestation)
        appointment2 = Appointment(user=self.user, subject="Deuxième RDV", 
                                 message="Deuxième massage", prestation=self.prestation)
        
        self.assertEqual(appointment1.prestation, self.prestation)
        self.assertEqual(appointment2.prestation, self.prestation)
        self.assertNotEqual(appointment1.id, appointment2.id)

    def test_appointment_belongs_to_one_prestation(self):
        # Un rendez-vous appartient à une seule prestation
        appointment = Appointment(user=self.user, subject="RDV massage", 
                                message="Massage relaxant", prestation=self.prestation)
        
        # Changer de prestation
        appointment.prestation = self.prestation2
        self.assertEqual(appointment.prestation, self.prestation2)
        self.assertEqual(appointment._prestation_id, self.prestation2.id)

    def test_different_prestations_different_appointments(self):
        # Différentes prestations peuvent avoir des rendez-vous
        appointment1 = Appointment(user=self.user, subject="Massage suédois", 
                                 message="Détente musculaire", prestation=self.prestation)
        appointment2 = Appointment(user=self.user, subject="Réflexologie", 
                                 message="Bien-être des pieds", prestation=self.prestation2)
        
        self.assertEqual(appointment1.prestation, self.prestation)
        self.assertEqual(appointment2.prestation, self.prestation2)
        self.assertNotEqual(appointment1._prestation_id, appointment2._prestation_id)

    def test_prestation_appointment_services_consistency(self):
        # Cohérence entre nom de prestation et sujet du RDV
        prestations_services = [
            (Prestation(name="Massage californien"), "Massage californien"),
            (Prestation(name="Aromathérapie"), "Séance aromathérapie"),
            (Prestation(name="Massage thérapeutique"), "Massage thérapeutique")
        ]
        
        appointments = []
        for prestation, subject in prestations_services:
            appointment = Appointment(user=self.user, subject=subject, 
                                    message="Rendez-vous bien-être", prestation=prestation)
            appointments.append(appointment)
            self.assertEqual(appointment.prestation, prestation)
        
        # Vérifier l'unicité des rendez-vous
        ids = [apt.id for apt in appointments]
        self.assertEqual(len(ids), len(set(ids)))

    def test_appointment_prestation_validation(self):
        # Test validation prestation requise
        with self.assertRaises(ValueError) as context:
            Appointment(user=self.user, subject="Test", message="Test", prestation=None)
        self.assertIn("Prestation is required", str(context.exception))


if __name__ == "__main__":
    unittest.main()