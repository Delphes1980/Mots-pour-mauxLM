#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.services.facade import Facade
from app.models.user import User
from app.models.prestation import Prestation


class TestFacadeSimple(BaseTest):
    """Tests pour la classe Facade sans mocks - utilise la vraie DB"""

    def setUp(self):
        super().setUp()
        self.facade = Facade()

    def test_facade_initialization(self):
        """Test que la façade initialise tous les services"""
        self.assertIsNotNone(self.facade.user_service)
        self.assertIsNotNone(self.facade.review_service)
        self.assertIsNotNone(self.facade.appointment_service)
        self.assertIsNotNone(self.facade.prestation_service)
        self.assertIsNotNone(self.facade.authentication_service)

    def test_facade_has_new_methods(self):
        """Test que la façade expose les nouvelles méthodes"""
        # Vérifier que les nouvelles méthodes existent
        self.assertTrue(hasattr(self.facade, 'admin_create_user'))
        self.assertTrue(hasattr(self.facade, 'search_users_by_email_fragment'))
        
        # Vérifier que ce sont des méthodes appelables
        self.assertTrue(callable(getattr(self.facade, 'admin_create_user')))
        self.assertTrue(callable(getattr(self.facade, 'search_users_by_email_fragment')))

    def test_create_user_delegation(self):
        """Test délégation create_user"""
        result = self.facade.create_user(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="Password123!"
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.first_name, "John")
        self.assertEqual(result.email, "john@example.com")

    def test_create_prestation_delegation(self):
        """Test délégation create_prestation"""
        result = self.facade.create_prestation(name="Massage Relaxant")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Massage Relaxant")

    def test_login_delegation(self):
        """Test délégation login"""
        # Créer un utilisateur d'abord
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        
        # Tester le login
        token = self.facade.login("test@example.com", "Password123!")
        
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_get_user_by_id_delegation(self):
        """Test délégation get_user_by_id"""
        # Créer un utilisateur d'abord
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        
        # Récupérer par ID
        result = self.facade.get_user_by_id(user.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.email, "test@example.com")

    def test_get_prestation_by_name_delegation(self):
        """Test délégation get_prestation_by_name"""
        # Créer une prestation d'abord
        prestation = self.facade.create_prestation(name="Massage Thérapeutique")
        
        # Récupérer par nom
        result = self.facade.get_prestation_by_name("Massage Thérapeutique")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Massage Thérapeutique")

    def test_update_user_delegation(self):
        """Test délégation update_user"""
        # Créer un utilisateur d'abord
        user = self.facade.create_user(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="Password123!"
        )
        
        # Mettre à jour
        result = self.facade.update_user(user.id, first_name="Jane")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.first_name, "Jane")
        self.assertEqual(result.last_name, "Doe")  # Inchangé

    def test_delete_user_delegation(self):
        """Test délégation delete_user"""
        # Créer le ghost user nécessaire à la suppression
        self.facade.create_user(
            first_name="Ghost",
            last_name="User",
            email="deleted@system.local",
            password="Ghost#2025!",
            is_admin=False
        )

        # Créer un utilisateur d'abord
        user = self.facade.create_user(
            first_name="ToDelete",
            last_name="User",
            email="delete@example.com",
            password="Password123!"
        )
        
        # Supprimer
        result = self.facade.delete_user(user.id)
        
        self.assertTrue(result)
        
        # Vérifier que l'utilisateur n'existe plus
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.facade.get_user_by_id(user.id)

    def test_get_user_by_email_delegation(self):
        """Test délégation get_user_by_email"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        
        result = self.facade.get_user_by_email("test@example.com")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.email, "test@example.com")

    def test_get_all_users_delegation(self):
        """Test délégation get_all_users"""
        user1 = self.facade.create_user(
            first_name="Jean",
            last_name="Dupont",
            email="user1@example.com",
            password="Password123!"
        )
        user2 = self.facade.create_user(
            first_name="Marie",
            last_name="Martin",
            email="user2@example.com",
            password="Password123!"
        )
        
        result = self.facade.get_all_users()
        
        self.assertEqual(len(result), 2)
        emails = [u.email for u in result]
        self.assertIn("user1@example.com", emails)
        self.assertIn("user2@example.com", emails)

    def test_change_password_delegation(self):
        """Test délégation change_password"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        
        result = self.facade.change_password(user.id, "Password123!", "NewPassword456!")
        
        self.assertIsNotNone(result)
        # Vérifier que le nouveau mot de passe fonctionne
        token = self.facade.login("test@example.com", "NewPassword456!")
        self.assertIsNotNone(token)

    def test_admin_reset_password_delegation(self):
        """Test délégation admin_reset_password"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        
        result = self.facade.admin_reset_password(user.id, "AdminReset456!")
        
        self.assertIsNotNone(result)
        # Vérifier que le nouveau mot de passe fonctionne
        token = self.facade.login("test@example.com", "AdminReset456!")
        self.assertIsNotNone(token)

    def test_get_prestation_by_id_delegation(self):
        """Test délégation get_prestation_by_id"""
        prestation = self.facade.create_prestation(name="Test Prestation")
        
        result = self.facade.get_prestation_by_id(prestation.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, prestation.id)
        self.assertEqual(result.name, "Test Prestation")

    def test_get_all_prestations_delegation(self):
        """Test délégation get_all_prestations"""
        prestation1 = self.facade.create_prestation(name="Massage Relaxant")
        prestation2 = self.facade.create_prestation(name="Massage Thérapeutique")
        
        result = self.facade.get_all_prestations()
        
        self.assertEqual(len(result), 2)
        names = [p.name for p in result]
        self.assertIn("Massage Relaxant", names)
        self.assertIn("Massage Thérapeutique", names)

    def test_update_prestation_delegation(self):
        """Test délégation update_prestation"""
        prestation = self.facade.create_prestation(name="Old Name")
        
        result = self.facade.update_prestation(prestation.id, name="New Name")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "New Name")

    def test_delete_prestation_delegation(self):
        """Test délégation delete_prestation"""
        ghost = Prestation(name="Ghost prestation")
        self.save_to_db(ghost)

        prestation = self.facade.create_prestation(name="To Delete")
        
        result = self.facade.delete_prestation(prestation.id)
        
        self.assertTrue(result)
        
        # Vérifier que la prestation n'existe plus
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.facade.get_prestation_by_id(prestation.id)

    def test_create_appointment_delegation(self):
        """Test délégation create_appointment"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        
        result = self.facade.create_appointment(
            message="Test appointment",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.message, "Test appointment")
        self.assertEqual(result.user_id, user.id)
        self.assertEqual(result.prestation_id, prestation.id)

    def test_get_appointment_by_id_delegation(self):
        """Test délégation get_appointment_by_id"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        appointment = self.facade.create_appointment(
            message="Test appointment",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.get_appointment_by_id(appointment.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, appointment.id)
        self.assertEqual(result.message, "Test appointment")

    def test_get_all_appointments_delegation(self):
        """Test délégation get_all_appointments"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        appointment1 = self.facade.create_appointment(
            message="Appointment 1",
            user_id=user.id,
            prestation_id=prestation.id
        )
        appointment2 = self.facade.create_appointment(
            message="Appointment 2",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.get_all_appointments()
        
        self.assertEqual(len(result), 2)
        messages = [a.message for a in result]
        self.assertIn("Appointment 1", messages)
        self.assertIn("Appointment 2", messages)

    def test_get_appointment_by_prestation_delegation(self):
        """Test délégation get_appointment_by_prestation"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        appointment = self.facade.create_appointment(
            message="Test appointment",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.get_appointment_by_prestation(prestation.id)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, appointment.id)

    def test_get_appointment_by_user_delegation(self):
        """Test délégation get_appointment_by_user"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        appointment = self.facade.create_appointment(
            message="Test appointment",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.get_appointment_by_user(user.id)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, appointment.id)

    def test_get_appointment_by_user_and_prestation_delegation(self):
        """Test délégation get_appointment_by_user_and_prestation"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        appointment = self.facade.create_appointment(
            message="Test appointment",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.get_appointment_by_user_and_prestation(user.id, prestation.id)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, appointment.id)

    def test_create_review_delegation(self):
        """Test délégation create_review"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        
        result = self.facade.create_review(
            rating=5,
            text="Excellent service",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.rating, 5)
        self.assertEqual(result.text, "Excellent service")
        self.assertEqual(result.user_id, user.id)
        self.assertEqual(result.prestation_id, prestation.id)

    def test_get_review_by_id_delegation(self):
        """Test délégation get_review_by_id"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        review = self.facade.create_review(
            rating=4,
            text="Good service",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.get_review_by_id(review.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, review.id)
        self.assertEqual(result.rating, 4)
        self.assertEqual(result.text, "Good service")

    def test_get_all_reviews_delegation(self):
        """Test délégation get_all_reviews"""
        user = self.facade.create_user(
            first_name="Jean",
            last_name="Dupont",
            email="test@example.com",
            password="Password123!"
        )
        prestation1 = self.facade.create_prestation(name="Massage Relaxant")
        prestation2 = self.facade.create_prestation(name="Massage Thérapeutique")
        review1 = self.facade.create_review(
            rating=5,
            text="Review 1",
            user_id=user.id,
            prestation_id=prestation1.id
        )
        review2 = self.facade.create_review(
            rating=4,
            text="Review 2",
            user_id=user.id,
            prestation_id=prestation2.id
        )
        
        result = self.facade.get_all_reviews()
        
        self.assertEqual(len(result), 2)
        texts = [r.text for r in result]
        self.assertIn("Review 1", texts)
        self.assertIn("Review 2", texts)

    def test_get_review_by_prestation_delegation(self):
        """Test délégation get_review_by_prestation"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        review = self.facade.create_review(
            rating=5,
            text="Great service",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.get_review_by_prestation(prestation.id)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, review.id)

    def test_get_review_by_user_delegation(self):
        """Test délégation get_review_by_user"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        review = self.facade.create_review(
            rating=5,
            text="Great service",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.get_review_by_user(user.id)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, review.id)

    def test_get_review_by_user_and_prestation_delegation(self):
        """Test délégation get_review_by_user_and_prestation"""
        user = self.facade.create_user(
            first_name="Jean",
            last_name="Dupont",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Massage Relaxant")
        review = self.facade.create_review(
            rating=5,
            text="Great service",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.get_review_by_user_and_prestation(user.id, prestation.id)
        
        # Cette méthode retourne un seul objet Review, pas une liste
        self.assertIsNotNone(result)
        self.assertEqual(result.id, review.id)

    def test_update_review_delegation(self):
        """Test délégation update_review"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        review = self.facade.create_review(
            rating=4,
            text="Good service",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.update_review(
            review.id,
            current_user_id=user.id,
            rating=5,
            text="Excellent service")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.rating, 5)
        self.assertEqual(result.text, "Excellent service")

    def test_delete_review_delegation(self):
        """Test délégation delete_review"""
        user = self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        prestation = self.facade.create_prestation(name="Test Prestation")
        review = self.facade.create_review(
            rating=5,
            text="To delete",
            user_id=user.id,
            prestation_id=prestation.id
        )
        
        result = self.facade.delete_review(review.id)
        
        self.assertTrue(result)
        
        # Vérifier que la review n'existe plus
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.facade.get_review_by_id(review.id)

    def test_admin_create_user_delegation(self):
        """Test délégation admin_create_user"""
        temp_password = "TempPassword123!"
        
        result = self.facade.admin_create_user(
            temp_password=temp_password,
            first_name="AdminCreated",
            last_name="User",
            email="admin.created@example.com",
            address="123 Admin St",
            phone_number="0123456789"
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.first_name, "AdminCreated")
        self.assertEqual(result.last_name, "User")
        self.assertEqual(result.email, "admin.created@example.com")
        self.assertEqual(result.address, "123 Admin St")
        self.assertEqual(result.phone_number, "0123456789")
        
        # Vérifier que le mot de passe temporaire fonctionne
        from app.utils import verify_password
        self.assertTrue(verify_password(result.password, temp_password))

    def test_admin_create_user_minimal_data_delegation(self):
        """Test délégation admin_create_user avec données minimales"""
        temp_password = "MinimalTemp456!"
        
        result = self.facade.admin_create_user(
            temp_password=temp_password,
            first_name="Minimal",
            last_name="User",
            email="minimal@example.com"
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.first_name, "Minimal")
        self.assertEqual(result.last_name, "User")
        self.assertEqual(result.email, "minimal@example.com")
        self.assertIsNone(result.address)
        self.assertIsNone(result.phone_number)
        
        # Vérifier que le mot de passe temporaire fonctionne
        from app.utils import verify_password
        self.assertTrue(verify_password(result.password, temp_password))

    def test_search_users_by_email_fragment_delegation(self):
        """Test délégation search_users_by_email_fragment"""
        # Créer des utilisateurs de test
        user1 = self.facade.create_user(
            first_name="John",
            last_name="Doe",
            email="john.doe@company.com",
            password="Password123!"
        )
        user2 = self.facade.create_user(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@company.com",
            password="Password456!"
        )
        user3 = self.facade.create_user(
            first_name="Bob",
            last_name="Johnson",
            email="bob@example.org",
            password="Password789!"
        )
        
        # Test recherche par domaine
        result = self.facade.search_users_by_email_fragment("company")
        
        self.assertEqual(len(result), 2)
        emails = [u.email for u in result]
        self.assertIn("john.doe@company.com", emails)
        self.assertIn("jane.smith@company.com", emails)
        self.assertNotIn("bob@example.org", emails)

    def test_search_users_by_email_fragment_single_result_delegation(self):
        """Test délégation search_users_by_email_fragment avec un seul résultat"""
        user = self.facade.create_user(
            first_name="Unique",
            last_name="User",
            email="unique.user@special.com",
            password="Password123!"
        )
        
        result = self.facade.search_users_by_email_fragment("unique")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].email, "unique.user@special.com")
        self.assertEqual(result[0].first_name, "Unique")

    def test_search_users_by_email_fragment_no_results_delegation(self):
        """Test délégation search_users_by_email_fragment sans résultats"""
        # Créer un utilisateur
        self.facade.create_user(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Password123!"
        )
        
        # Rechercher quelque chose qui n'existe pas
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.facade.search_users_by_email_fragment("nonexistent")
        
        self.assertIn("No user found", str(context.exception))

    def test_admin_create_user_and_search_integration_delegation(self):
        """Test intégration admin_create_user et search_users_by_email_fragment via facade"""
        # Créer des utilisateurs via admin
        admin_user1 = self.facade.admin_create_user(
            temp_password="AdminTemp1!",
            first_name="AdminUser1",
            last_name="Test",
            email="admin.user1@test.com"
        )
        admin_user2 = self.facade.admin_create_user(
            temp_password="AdminTemp2!",
            first_name="AdminUser2",
            last_name="Test",
            email="admin.user2@test.com"
        )
        
        # Créer un utilisateur normal
        normal_user = self.facade.create_user(
            first_name="NormalUser",
            last_name="Test",
            email="normal.user@test.com",
            password="NormalPass123!"
        )
        
        # Rechercher tous les utilisateurs test.com
        result = self.facade.search_users_by_email_fragment("test.com")
        
        self.assertEqual(len(result), 3)
        emails = [u.email for u in result]
        self.assertIn("admin.user1@test.com", emails)
        self.assertIn("admin.user2@test.com", emails)
        self.assertIn("normal.user@test.com", emails)
        
        # Rechercher spécifiquement les utilisateurs admin
        admin_result = self.facade.search_users_by_email_fragment("admin.user")
        
        self.assertEqual(len(admin_result), 2)
        admin_emails = [u.email for u in admin_result]
        self.assertIn("admin.user1@test.com", admin_emails)
        self.assertIn("admin.user2@test.com", admin_emails)
        self.assertNotIn("normal.user@test.com", admin_emails)


if __name__ == '__main__':
    unittest.main()