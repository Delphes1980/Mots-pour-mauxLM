import unittest
from app.tests.base_test import BaseTest
from app.services.PrestationService import PrestationService
from app.models.prestation import Prestation


class TestPrestationService(BaseTest):
    """Tests d'intégration pour PrestationService"""

    def setUp(self):
        super().setUp()
        self.service = PrestationService()
        # S'assurer que le repository utilise la même instance de db
        self.service.prestation_repository.db = self.db

    # ==================== Tests create_prestation ====================

    def test_create_prestation_success(self):
        """Test de création réussie d'une prestation"""
        result = self.service.create_prestation(name="Massage relaxant")
        
        self.assertIsInstance(result, Prestation)
        self.assertEqual(result.name, "Massage relaxant")
        self.assertIsNotNone(result.id)

    def test_create_prestation_duplicate_name(self):
        """Test création prestation avec nom existant"""
        self.service.create_prestation(name="Massage")
        
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.create_prestation(name="Massage")
        self.assertIn("existe déjà", str(context.exception).lower())

    def test_create_prestation_invalid_name_empty(self):
        """Test avec nom vide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.service.create_prestation(name="")

    def test_create_prestation_invalid_name_none(self):
        """Test avec nom None"""
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.service.create_prestation(name=None)

    def test_create_prestation_invalid_name_too_long(self):
        """Test avec nom trop long"""
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.service.create_prestation(name="A" * 51)

    def test_create_prestation_missing_name(self):
        """Test sans nom"""
        with self.assertRaises(TypeError):
            self.service.create_prestation()

    # ==================== Tests get_prestation_by_id ====================

    def test_get_prestation_by_id_success(self):
        """Test de récupération réussie d'une prestation par ID"""
        created_prestation = self.service.create_prestation(name="Thérapie")
        
        result = self.service.get_prestation_by_id(created_prestation.id)
        
        self.assertEqual(result.id, created_prestation.id)
        self.assertEqual(result.name, "Thérapie")

    def test_get_prestation_by_id_missing_id(self):
        """Test sans ID"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.get_prestation_by_id(None)
        self.assertIn("prestation_id", str(context.exception).lower())

    def test_get_prestation_by_id_invalid_format(self):
        """Test avec un format d'ID invalide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.get_prestation_by_id('invalid-uuid')
        self.assertIn("format", str(context.exception).lower())

    def test_get_prestation_by_id_not_found(self):
        """Test quand la prestation n'existe pas"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.get_prestation_by_id('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        self.assertIn("non trouvée", str(context.exception).lower())

    # ==================== Tests get_all_prestations ====================

    def test_get_all_prestations_with_data(self):
        """Test de récupération de toutes les prestations"""
        prestation1 = self.service.create_prestation(name="Massage")
        prestation2 = self.service.create_prestation(name="Thérapie")
        
        result = self.service.get_all_prestations()
        
        self.assertEqual(len(result), 2)
        prestation_ids = [p.id for p in result]
        self.assertIn(prestation1.id, prestation_ids)
        self.assertIn(prestation2.id, prestation_ids)

    def test_get_all_prestations_empty(self):
        """Test quand il n'y a aucune prestation"""
        result = self.service.get_all_prestations()
        self.assertEqual(result, [])

    # ==================== Tests get_prestation_by_name ====================

    def test_get_prestation_by_name_success(self):
        """Test de récupération réussie d'une prestation par nom"""
        created_prestation = self.service.create_prestation(name="Consultation")
        
        result = self.service.get_prestation_by_name("Consultation")
        
        self.assertEqual(result.id, created_prestation.id)
        self.assertEqual(result.name, "Consultation")

    def test_get_prestation_by_name_missing_name(self):
        """Test sans nom"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.get_prestation_by_name(None)
        self.assertIn("requis", str(context.exception).lower())

    def test_get_prestation_by_name_empty_name(self):
        """Test avec nom vide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.get_prestation_by_name("")
        self.assertIn("requis", str(context.exception).lower())

    def test_get_prestation_by_name_not_found(self):
        """Test quand la prestation n'existe pas"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.get_prestation_by_name("Inexistante")
        self.assertIn("non trouvée", str(context.exception).lower())

    # ==================== Tests update_prestation ====================

    def test_update_prestation_success(self):
        """Test de mise à jour réussie d'une prestation"""
        created_prestation = self.service.create_prestation(name="Ancien nom")
        
        result = self.service.update_prestation(created_prestation.id, name="Nouveau nom")
        
        self.assertEqual(result.name, "Nouveau nom")
        self.assertEqual(result.id, created_prestation.id)

    def test_update_prestation_missing_id(self):
        """Test sans prestation_id"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.update_prestation(None, name="Nouveau nom")
        self.assertIn("prestation_id", str(context.exception).lower())

    def test_update_prestation_invalid_id_format(self):
        """Test avec un format d'ID invalide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.update_prestation('invalid-uuid', name="Nouveau nom")
        self.assertIn("format", str(context.exception).lower())

    def test_update_prestation_not_found(self):
        """Test quand la prestation n'existe pas"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.update_prestation('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', name="Nouveau nom")
        self.assertIn("non trouvée", str(context.exception).lower())

    def test_update_prestation_no_data(self):
        """Test sans données à mettre à jour"""
        created_prestation = self.service.create_prestation(name="Test")
        
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.update_prestation(created_prestation.id)
        self.assertIn("aucune donnée", str(context.exception).lower())

    def test_update_prestation_duplicate_name(self):
        """Test mise à jour avec nom déjà existant"""
        prestation1 = self.service.create_prestation(name="Massage")
        prestation2 = self.service.create_prestation(name="Thérapie")
        
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.update_prestation(prestation2.id, name="Massage")
        self.assertIn("déjà existante", str(context.exception).lower())

    def test_update_prestation_same_name(self):
        """Test mise à jour avec le même nom (autorisé)"""
        created_prestation = self.service.create_prestation(name="Massage")
        
        result = self.service.update_prestation(created_prestation.id, name="Massage")
        
        self.assertEqual(result.name, "Massage")
        self.assertEqual(result.id, created_prestation.id)

    def test_update_prestation_invalid_name(self):
        """Test mise à jour avec nom invalide"""
        created_prestation = self.service.create_prestation(name="Test")
        
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.service.update_prestation(created_prestation.id, name="")

    # ==================== Tests delete_prestation ====================

    def test_delete_prestation_success(self):
        """Test de suppression réussie d'une prestation"""
        created_prestation = self.service.create_prestation(name="À supprimer")
        
        result = self.service.delete_prestation(created_prestation.id)
        
        self.assertTrue(result)
        
        # Vérifier que la prestation n'existe plus
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.service.get_prestation_by_id(created_prestation.id)

    def test_delete_prestation_missing_id(self):
        """Test sans prestation_id"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.delete_prestation(None)
        self.assertIn("prestation_id", str(context.exception).lower())

    def test_delete_prestation_invalid_id_format(self):
        """Test avec un format d'ID invalide"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.delete_prestation('invalid-uuid')
        self.assertIn("format", str(context.exception).lower())

    def test_delete_prestation_not_found(self):
        """Test quand la prestation n'existe pas"""
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.delete_prestation('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        self.assertIn("non trouvée", str(context.exception).lower())


if __name__ == '__main__':
    unittest.main()