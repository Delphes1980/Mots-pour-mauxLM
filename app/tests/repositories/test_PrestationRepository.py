import unittest
from sqlalchemy.exc import SQLAlchemyError
from app.tests.base_test import BaseTest
from app.models.prestation import Prestation
from app.persistence.PrestationRepository import PrestationRepository


class TestPrestationRepository(BaseTest):
    def setUp(self):
        super().setUp()
        self.prestation_repo = PrestationRepository()
        # Forcer l'utilisation de l'instance DB de test
        self.prestation_repo.db = self.db

    def test_create_prestation_success(self):
        """Test création prestation réussie"""
        prestation = self.prestation_repo.create(name="Massage suédois")
        
        self.assertIsNotNone(prestation.id)
        self.assertEqual(prestation.name, "Massage suédois")

    def test_create_prestation_duplicate_name(self):
        """Test création prestation avec nom existant"""
        # Créer première prestation
        self.prestation_repo.create(name="Massage thérapeutique")
        
        # Tenter de créer une autre avec même nom
        with self.assertRaises(ValueError):
            self.prestation_repo.create(name="Massage thérapeutique")

    def test_get_prestation_by_name_existing(self):
        """Test récupération prestation par nom existant"""
        # Créer prestation
        created_prestation = self.prestation_repo.create(name="Réflexologie")
        
        # Récupérer par nom
        found_prestation = self.prestation_repo.get_by_attribute("name", "Réflexologie")
        
        self.assertIsNotNone(found_prestation)
        self.assertEqual(found_prestation.id, created_prestation.id)
        self.assertEqual(found_prestation.name, "Réflexologie")

    def test_get_prestation_by_name_not_found(self):
        """Test récupération prestation par nom inexistant"""
        prestation = self.prestation_repo.get_by_attribute("name", "Inexistant")
        self.assertIsNone(prestation)

    def test_get_prestation_by_name_case_sensitive(self):
        """Test que la recherche par nom est sensible à la casse"""
        # Créer prestation
        self.prestation_repo.create(name="Aromathérapie")
        
        # Rechercher avec casse différente
        found_lower = self.prestation_repo.get_by_attribute("name", "aromathérapie")
        found_upper = self.prestation_repo.get_by_attribute("name", "AROMATHÉRAPIE")
        
        self.assertIsNone(found_lower)
        self.assertIsNone(found_upper)

    def test_multiple_prestations_creation(self):
        """Test création de plusieurs prestations différentes"""
        prestations_names = [
            "Massage californien",
            "Massage deep tissue", 
            "Shiatsu",
            "Réflexologie plantaire"
        ]
        
        created_prestations = []
        for name in prestations_names:
            prestation = self.prestation_repo.create(name=name)
            created_prestations.append(prestation)
            self.assertEqual(prestation.name, name)
        
        # Vérifier que toutes ont des IDs uniques
        ids = [p.id for p in created_prestations]
        self.assertEqual(len(ids), len(set(ids)))

    def test_prestation_name_validation(self):
        """Test validation du nom de prestation"""
        # Test nom vide
        with self.assertRaises(ValueError):
            self.prestation_repo.create(name="")
        
        # Test nom None
        with self.assertRaises(ValueError):
            self.prestation_repo.create(name=None)
        
        # Test nom trop long (> 100 caractères)
        long_name = "A" * 101
        with self.assertRaises(ValueError):
            self.prestation_repo.create(name=long_name)

    def test_inheritance_from_base_repository(self):
        """Test que PrestationRepository hérite bien de BaseRepository"""
        # Test méthodes héritées avec create
        prestation = self.prestation_repo.create(name="Test héritage")
        self.assertIsNotNone(prestation.id)
        
        # Test get_by_id (méthode héritée)
        found_prestation = self.prestation_repo.get_by_id(prestation.id)
        self.assertEqual(found_prestation.id, prestation.id)
        
        # Test get_all (méthode héritées)
        all_prestations = self.prestation_repo.get_all()
        self.assertIn(prestation, all_prestations)
        
        # Test update (méthode héritée)
        updated_prestation = self.prestation_repo.update(prestation.id, name="Nom mis à jour")
        self.assertEqual(updated_prestation.name, "Nom mis à jour")
        
        # Test delete (méthode héritée)
        result = self.prestation_repo.delete(prestation.id)
        self.assertTrue(result)
        
        # Vérifier suppression
        deleted_prestation = self.prestation_repo.get_by_id(prestation.id)
        self.assertIsNone(deleted_prestation)

    def test_get_all_prestations(self):
        """Test récupération de toutes les prestations"""
        # Créer plusieurs prestations
        prestation1 = self.prestation_repo.create(name="Massage suédois")
        prestation2 = self.prestation_repo.create(name="Réflexologie")
        prestation3 = self.prestation_repo.create(name="Aromathérapie")
        
        # Récupérer toutes
        all_prestations = self.prestation_repo.get_all()
        
        self.assertEqual(len(all_prestations), 3)
        prestation_ids = [p.id for p in all_prestations]
        self.assertIn(prestation1.id, prestation_ids)
        self.assertIn(prestation2.id, prestation_ids)
        self.assertIn(prestation3.id, prestation_ids)

    def test_get_all_empty(self):
        """Test get_all() quand aucune prestation n'existe"""
        all_prestations = self.prestation_repo.get_all()
        self.assertEqual(len(all_prestations), 0)

    def test_model_class_consistency(self):
        """Test que model_class est bien configuré"""
        self.assertEqual(self.prestation_repo.model_class, Prestation)

    def test_prestation_with_special_characters(self):
        """Test création prestation avec caractères spéciaux"""
        special_names = [
            "Massage à l'huile d'argan",
            "Thérapie énergétique",
            "Soin visage anti-âge",
            "Massage pré/post-natal"
        ]
        
        for name in special_names:
            prestation = self.prestation_repo.create(name=name)
            self.assertEqual(prestation.name, name)
            
            # Vérifier récupération
            found = self.prestation_repo.get_by_attribute("name", name)
            self.assertIsNotNone(found)
            self.assertEqual(found.name, name)

    def test_prestation_name_trimming(self):
        """Test que les espaces en début/fin sont supprimés"""
        prestation = self.prestation_repo.create(name="  Massage relaxant  ")
        self.assertEqual(prestation.name, "Massage relaxant")
        
        # Vérifier récupération avec nom trimé
        found = self.prestation_repo.get_by_attribute("name", "Massage relaxant")
        self.assertIsNotNone(found)


if __name__ == "__main__":
    unittest.main()