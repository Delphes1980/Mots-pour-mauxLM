import unittest
from app.tests.base_test import BaseTest
from app.models.prestation import Prestation
from app.models.appointment import Appointment
from app.models.review import Review
from app.models.user import User


class TestPrestation(BaseTest):

    def test_prestation_creation_valid(self):
        # Test création valide
        prestation = Prestation(name="Massage suédois")
        self.assertEqual(prestation.name, "Massage suédois")
        self.assertIsNotNone(prestation.id)

    def test_prestation_name_validation_none(self):
        # Test nom None
        with self.assertRaises(ValueError) as context:
            Prestation(name=None)
        self.assertIn("Expected name but received None", str(context.exception))

    def test_prestation_name_validation_wrong_type(self):
        # Test mauvais type
        with self.assertRaises(TypeError) as context:
            Prestation(name=123)
        self.assertIn("name must be of type str", str(context.exception))

    def test_prestation_name_validation_empty(self):
        # Test nom vide
        with self.assertRaises(ValueError) as context:
            Prestation(name="")
        self.assertIn("name must be shorter than 50 characters and include at least 1 no-space characters", str(context.exception))

    def test_prestation_name_validation_too_long(self):
        # Test nom trop long
        long_name = "a" * 51
        with self.assertRaises(ValueError) as context:
            Prestation(name=long_name)
        self.assertIn("name must be shorter than 50 characters and include at least 1 no-space characters", str(context.exception))

    def test_prestation_name_validation_whitespace_trim(self):
        # Test suppression espaces
        prestation = Prestation(name="  Aromathérapie  ")
        self.assertEqual(prestation.name, "Aromathérapie")

    def test_prestation_name_setter(self):
        # Test modification nom
        prestation = Prestation(name="Massage")
        prestation.name = "Réflexologie"
        self.assertEqual(prestation.name, "Réflexologie")

    def test_prestation_name_setter_validation(self):
        # Test validation lors modification
        prestation = Prestation(name="Massage")
        with self.assertRaises(ValueError) as context:
            prestation.name = ""
        self.assertIn("name must be shorter than 50 characters and include at least 1 no-space characters", str(context.exception))

    def test_prestation_different_services(self):
        # Test différents types de prestations
        services = [
            "Massage suédois",
            "Réflexologie plantaire", 
            "Aromathérapie",
            "Massage thérapeutique",
            "Massage californien"
        ]
        
        prestations = []
        for service in services:
            prestation = Prestation(name=service)
            prestations.append(prestation)
            self.assertEqual(prestation.name, service)
        
        # Vérifier unicité des IDs
        ids = [p.id for p in prestations]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()