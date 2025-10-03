import unittest
from app.tests.base_test import BaseTest
from app.services.UserService import UserService
from app.persistence.UserRepository import UserRepository
from app.models.user import User


class TestUserServiceIntegration(BaseTest):
    """Tests d'intégration pour UserService avec vraie base de données"""

    def setUp(self):
        super().setUp()
        self.user_repo = UserRepository()
        self.user_service = UserService()

    def test_create_user_full_integration(self):
        """Test d'intégration complet création d'utilisateur"""
        user = self.user_service.create_user(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            password="Password123!",
            address="123 Rue de la Paix",
            phone_number="+33123456789"
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.first_name, "Jean")
        self.assertEqual(user.last_name, "Dupont")
        self.assertEqual(user.email, "jean.dupont@example.com")
        self.assertEqual(user.address, "123 Rue de la Paix")
        self.assertEqual(user.phone_number, "+33123456789")
        self.assertFalse(user.is_admin)
        
        # Vérifier que l'utilisateur est bien en base
        saved_user = self.user_repo.get_by_id(user.id)
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.email, "jean.dupont@example.com")

    def test_user_workflow_integration(self):
        """Test d'intégration workflow complet de gestion des utilisateurs"""
        # Créer plusieurs utilisateurs
        user1 = self.user_service.create_user(
            first_name="Marie",
            last_name="Martin",
            email="marie@example.com",
            password="Password123!"
        )
        
        user2 = self.user_service.create_user(
            first_name="Pierre",
            last_name="Durand",
            email="pierre@example.com",
            password="Password456!",
            is_admin=True
        )
        
        # Récupérer tous les utilisateurs
        all_users = self.user_service.get_all_users()
        self.assertEqual(len(all_users), 2)
        
        # Récupérer par email
        found_user = self.user_service.get_user_by_email("marie@example.com")
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.first_name, "Marie")
        
        # Mettre à jour un utilisateur
        updated_user = self.user_service.update_user(
            user1.id,
            first_name="Marie-Claire",
            address="456 Avenue des Champs"
        )
        self.assertEqual(updated_user.first_name, "Marie-Claire")
        self.assertEqual(updated_user.address, "456 Avenue des Champs")
        
        # Supprimer un utilisateur
        result = self.user_service.delete_user(user2.id)
        self.assertTrue(result)
        
        # Vérifier que l'utilisateur est supprimé
        with self.assertRaises(ValueError) as context:
            self.user_service.get_user_by_id(user2.id)
        self.assertIn("User not found", str(context.exception))

    def test_user_data_integrity_integration(self):
        """Test d'intégration intégrité des données"""
        # Créer utilisateur avec données complètes
        user = self.user_service.create_user(
            first_name="François-Xavier",
            last_name="De La Fontaine",
            email="fx.delafontaine@example.com",
            password="ComplexPass123!",
            address="789 Boulevard Saint-Germain, 75007 Paris",
            phone_number="+33 1 42 34 56 78"
        )
        
        # Vérifier l'intégrité des données
        self.assertEqual(user.first_name, "François-Xavier")
        self.assertEqual(user.last_name, "De La Fontaine")
        self.assertTrue(user.password.startswith('$2b$'))  # Hash bcrypt
        
        # Récupérer depuis la base et vérifier
        saved_user = self.user_repo.get_by_id(user.id)
        self.assertEqual(saved_user.address, "789 Boulevard Saint-Germain, 75007 Paris")
        self.assertEqual(saved_user.phone_number, "+33 1 42 34 56 78")

    def test_user_edge_cases_integration(self):
        """Test d'intégration cas limites"""
        # Utilisateur avec données minimales
        minimal_user = self.user_service.create_user(
            first_name="Ana",
            last_name="Silva",
            email="ana@example.com",
            password="MinPass123!"
        )
        
        self.assertIsNone(minimal_user.address)
        self.assertIsNone(minimal_user.phone_number)
        self.assertFalse(minimal_user.is_admin)
        
        # Utilisateur admin
        admin_user = self.user_service.create_user(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="AdminPass123!",
            is_admin=True
        )
        
        self.assertTrue(admin_user.is_admin)
        
        # Vérifier unicité email
        with self.assertRaises(ValueError) as context:
            self.user_service.create_user(
                first_name="Duplicate",
                last_name="Email",
                email="ana@example.com",  # Email déjà utilisé
                password="Password123!"
            )
        
        self.assertIn("Email already exists", str(context.exception))

    def test_multiple_users_same_name_integration(self):
        """Test d'intégration plusieurs utilisateurs même nom"""
        # Créer plusieurs utilisateurs avec même nom mais emails différents
        user1 = self.user_service.create_user(
            first_name="Jean",
            last_name="Martin",
            email="jean.martin1@example.com",
            password="Password123!"
        )
        
        user2 = self.user_service.create_user(
            first_name="Jean",
            last_name="Martin",
            email="jean.martin2@example.com",
            password="Password456!"
        )
        
        # Vérifier que les deux utilisateurs existent
        all_users = self.user_service.get_all_users()
        jean_martins = [u for u in all_users if u.first_name == "Jean" and u.last_name == "Martin"]
        self.assertEqual(len(jean_martins), 2)
        
        # Vérifier qu'ils ont des IDs différents
        self.assertNotEqual(user1.id, user2.id)
        
        # Vérifier récupération par email
        found_user1 = self.user_service.get_user_by_email("jean.martin1@example.com")
        found_user2 = self.user_service.get_user_by_email("jean.martin2@example.com")
        
        self.assertEqual(found_user1.id, user1.id)
        self.assertEqual(found_user2.id, user2.id)


if __name__ == '__main__':
    unittest.main()