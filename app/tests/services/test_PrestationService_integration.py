import unittest
from app.tests.base_test import BaseTest
from app.services.PrestationService import PrestationService


class TestPrestationServiceIntegration(BaseTest):
    """Tests d'intégration pour PrestationService avec vraie base de données"""

    def setUp(self):
        super().setUp()
        self.service = PrestationService()
        self.service.prestation_repository.db = self.db

    def test_full_prestation_lifecycle(self):
        """Test cycle complet : création, lecture, mise à jour, suppression"""
        # Création
        prestation = self.service.create_prestation(name="Massage suédois")
        
        self.assertIsNotNone(prestation.id)
        self.assertEqual(prestation.name, "Massage suédois")
        
        # Lecture par ID
        retrieved_prestation = self.service.get_prestation_by_id(prestation.id)
        self.assertEqual(retrieved_prestation.name, "Massage suédois")
        
        # Lecture par nom
        found_prestation = self.service.get_prestation_by_name("Massage suédois")
        self.assertEqual(found_prestation.id, prestation.id)
        
        # Mise à jour
        updated_prestation = self.service.update_prestation(prestation.id, name="Massage thérapeutique")
        self.assertEqual(updated_prestation.name, "Massage thérapeutique")
        
        # Vérifier que l'ancien nom ne fonctionne plus
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.service.get_prestation_by_name("Massage suédois")
        
        # Suppression
        result = self.service.delete_prestation(prestation.id)
        self.assertTrue(result)
        
        # Vérification suppression
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.service.get_prestation_by_id(prestation.id)

    def test_business_rule_unique_name(self):
        """Test règle métier : nom unique"""
        # Première prestation
        self.service.create_prestation(name="Réflexologie")
        
        # Tentative de création avec même nom
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.create_prestation(name="Réflexologie")
        
        self.assertIn("existe déjà", str(context.exception))

    def test_multiple_prestations_management(self):
        """Test gestion de plusieurs prestations"""
        # Créer plusieurs prestations
        prestation1 = self.service.create_prestation(name="Massage californien")
        prestation2 = self.service.create_prestation(name="Aromathérapie")
        prestation3 = self.service.create_prestation(name="Shiatsu")
        
        # Récupérer toutes les prestations
        all_prestations = self.service.get_all_prestations()
        
        self.assertEqual(len(all_prestations), 3)
        names = [p.name for p in all_prestations]
        self.assertIn("Massage californien", names)
        self.assertIn("Aromathérapie", names)
        self.assertIn("Shiatsu", names)
        
        # Supprimer une prestation
        self.service.delete_prestation(prestation2.id)
        
        # Vérifier qu'il en reste 2
        remaining_prestations = self.service.get_all_prestations()
        self.assertEqual(len(remaining_prestations), 2)
        remaining_names = [p.name for p in remaining_prestations]
        self.assertNotIn("Aromathérapie", remaining_names)

    def test_update_to_existing_name_different_prestation(self):
        """Test mise à jour vers nom existant d'une autre prestation"""
        # Créer deux prestations
        prestation1 = self.service.create_prestation(name="Massage A")
        prestation2 = self.service.create_prestation(name="Massage B")
        
        # Tenter de donner à prestation2 le nom de prestation1
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.update_prestation(prestation2.id, name="Massage A")
        
        self.assertIn("déjà existante", str(context.exception))

    def test_update_same_name_allowed(self):
        """Test mise à jour avec le même nom (autorisé)"""
        prestation = self.service.create_prestation(name="Massage relaxant")
        
        # Mettre à jour avec le même nom
        updated_prestation = self.service.update_prestation(prestation.id, name="Massage relaxant")
        
        self.assertEqual(updated_prestation.name, "Massage relaxant")
        self.assertEqual(updated_prestation.id, prestation.id)


if __name__ == '__main__':
    unittest.main()