import unittest
from unittest.mock import Mock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.tests.base_test import BaseTest
from app.models.user import User
from app.services.UserService import UserService
from app.persistence.UserRepository import UserRepository


class TestUserService(BaseTest):
    def setUp(self):
        super().setUp()
        self.user_service = UserService()
        # Forcer l'utilisation de l'instance DB de test
        self.user_service.user_repository.db = self.db

    def test_create_user_success(self):
        """Test création utilisateur réussie"""
        user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'Password123!',
            'address': '123 Main St',
            'phone_number': '0123456789'
        }
        
        user = self.user_service.create_user(**user_data)
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'john@example.com')
        self.assertEqual(user.address, '123 Main St')
        self.assertEqual(user.phone_number, '0123456789')
        self.assertFalse(user.is_admin)

    def test_create_user_minimal_data(self):
        """Test création utilisateur avec données minimales"""
        user_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'password': 'Password123!',
            'address': None,
            'phone_number': None
        }
        
        user = self.user_service.create_user(**user_data)
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Smith')
        self.assertEqual(user.email, 'jane@example.com')
        self.assertIsNone(user.address)
        self.assertIsNone(user.phone_number)
        self.assertFalse(user.is_admin)

    def test_create_user_admin(self):
        """Test création utilisateur admin"""
        user_data = {
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin@example.com',
            'password': 'Password123!',
            'address': None,
            'phone_number': None,
            'is_admin': True
        }
        
        user = self.user_service.create_user(**user_data)
        
        self.assertTrue(user.is_admin)

    def test_create_user_duplicate_email(self):
        """Test création utilisateur avec email existant"""
        # Créer premier utilisateur
        self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Tenter de créer un autre avec même email
        with self.assertRaises(ValueError) as context:
            self.user_service.create_user(
                first_name='Jane',
                last_name='Smith',
                email='john@example.com',
                password='Password456!'
            )
        
        self.assertIn('Email already exists', str(context.exception))

    def test_create_user_invalid_data(self):
        """Test création utilisateur avec données invalides"""
        # Test email invalide
        with self.assertRaises(ValueError):
            self.user_service.create_user(
                first_name='John',
                last_name='Doe',
                email='invalid-email',
                password='Password123!'
            )
        
        # Test mot de passe invalide
        with self.assertRaises(ValueError):
            self.user_service.create_user(
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                password='weak'
            )

    def test_get_user_by_id_existing(self):
        """Test récupération utilisateur par ID existant"""
        # Créer utilisateur
        created_user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Récupérer par ID
        found_user = self.user_service.get_user_by_id(created_user.id)
        
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.id, created_user.id)
        self.assertEqual(found_user.email, 'john@example.com')

    def test_get_user_by_id_not_found(self):
        """Test récupération utilisateur par ID inexistant"""
        with self.assertRaises(ValueError) as context:
            self.user_service.get_user_by_id('nonexistent-id')
        
        self.assertIn('user_id', str(context.exception).lower())

    def test_get_user_by_email_existing(self):
        """Test récupération utilisateur par email existant"""
        # Créer utilisateur
        created_user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Récupérer par email
        found_user = self.user_service.get_user_by_email('john@example.com')
        
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.id, created_user.id)
        self.assertEqual(found_user.email, 'john@example.com')

    def test_get_user_by_email_not_found(self):
        """Test récupération utilisateur par email inexistant"""
        with self.assertRaises(ValueError) as context:
            self.user_service.get_user_by_email('nonexistent@example.com')
        
        self.assertIn('User not found', str(context.exception))

    def test_get_all_users(self):
        """Test récupération de tous les utilisateurs"""
        # Créer plusieurs utilisateurs
        user1 = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        user2 = self.user_service.create_user(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            password='Password456!'
        )
        
        # Récupérer tous
        all_users = self.user_service.get_all_users()
        
        self.assertEqual(len(all_users), 2)
        user_ids = [u.id for u in all_users]
        self.assertIn(user1.id, user_ids)
        self.assertIn(user2.id, user_ids)

    def test_get_all_users_empty(self):
        """Test get_all_users() quand aucun utilisateur n'existe"""
        all_users = self.user_service.get_all_users()
        self.assertEqual(len(all_users), 0)

    def test_update_user_first_name_only(self):
        """Test mise à jour du prénom seulement"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St',
            phone_number='0123456789'
        )
        
        # Mettre à jour prénom seulement
        updated_user = self.user_service.update_user(user.id, first_name='Johnny')
        
        self.assertEqual(updated_user.first_name, 'Johnny')
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        self.assertEqual(updated_user.address, '123 Main St')  # Inchangé
        self.assertEqual(updated_user.phone_number, '0123456789')  # Inchangé

    def test_update_user_last_name_only(self):
        """Test mise à jour du nom seulement"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Mettre à jour nom seulement
        updated_user = self.user_service.update_user(user.id, last_name='Smith')
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Smith')
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé

    def test_update_user_email_only(self):
        """Test mise à jour de l'email seulement"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Mettre à jour email seulement
        updated_user = self.user_service.update_user(user.id, email='john.doe@example.com')
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john.doe@example.com')

    def test_update_user_address_only(self):
        """Test mise à jour de l'adresse seulement"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St',
            phone_number=None
        )
        
        # Mettre à jour adresse seulement
        updated_user = self.user_service.update_user(user.id, address='456 Oak Ave')
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        self.assertEqual(updated_user.address, '456 Oak Ave')

    def test_update_user_phone_number_only(self):
        """Test mise à jour du téléphone seulement"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address=None,
            phone_number='0123456789'
        )
        
        # Mettre à jour téléphone seulement
        updated_user = self.user_service.update_user(user.id, phone_number='0987654321')
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        self.assertEqual(updated_user.phone_number, '0987654321')

    def test_update_user_is_admin_only(self):
        """Test mise à jour du statut admin seulement"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Mettre à jour statut admin seulement
        updated_user = self.user_service.update_user(user.id, is_admin=True)
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        self.assertTrue(updated_user.is_admin)

    def test_update_user_password_only(self):
        """Test mise à jour du mot de passe seulement"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Vérifier ancien mot de passe
        self.assertTrue(user.verify_password('Password123!'))
        
        # Mettre à jour mot de passe seulement
        updated_user = self.user_service.update_user(user.id, password='NewPassword456!')
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        # Vérifier nouveau mot de passe
        self.assertTrue(updated_user.verify_password('NewPassword456!'))
        self.assertFalse(updated_user.verify_password('Password123!'))

    def test_update_user_invalid_password(self):
        """Test mise à jour avec mot de passe invalide"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Tenter mise à jour avec mot de passe invalide
        with self.assertRaises(ValueError):
            self.user_service.update_user(user.id, password='weak')

    def test_update_user_password_validation_requirements(self):
        """Test validation des exigences du mot de passe lors mise à jour"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Test mot de passe trop court
        with self.assertRaises(ValueError):
            self.user_service.update_user(user.id, password='Short1!')
        
        # Test mot de passe sans chiffre
        with self.assertRaises(ValueError):
            self.user_service.update_user(user.id, password='NoDigitPassword!')
        
        # Test mot de passe sans caractère spécial
        with self.assertRaises(ValueError):
            self.user_service.update_user(user.id, password='NoSpecialChar123')
        
        # Vérifier que l'ancien mot de passe fonctionne toujours
        self.assertTrue(user.verify_password('Password123!'))

    def test_update_user_password_with_other_fields(self):
        """Test mise à jour du mot de passe avec d'autres champs"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Mettre à jour nom et mot de passe
        updated_user = self.user_service.update_user(
            user.id,
            first_name='Johnny',
            password='SuperSecure456!'
        )
        
        self.assertEqual(updated_user.first_name, 'Johnny')
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        # Vérifier nouveau mot de passe
        self.assertTrue(updated_user.verify_password('SuperSecure456!'))
        self.assertFalse(updated_user.verify_password('Password123!'))

    def test_update_user_multiple_fields(self):
        """Test mise à jour de plusieurs champs en même temps"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St',
            phone_number='0123456789'
        )
        
        # Mettre à jour plusieurs champs
        updated_user = self.user_service.update_user(
            user.id,
            first_name='Johnny',
            last_name='Smith',
            email='johnny.smith@example.com',
            password='NewPassword456!',
            address='789 Pine St',
            phone_number='0555123456',
            is_admin=True
        )
        
        self.assertEqual(updated_user.first_name, 'Johnny')
        self.assertEqual(updated_user.last_name, 'Smith')
        self.assertEqual(updated_user.email, 'johnny.smith@example.com')
        self.assertEqual(updated_user.address, '789 Pine St')
        self.assertEqual(updated_user.phone_number, '0555123456')
        self.assertTrue(updated_user.is_admin)
        # Vérifier nouveau mot de passe
        self.assertTrue(updated_user.verify_password('NewPassword456!'))
        self.assertFalse(updated_user.verify_password('Password123!'))

    def test_update_user_partial_fields(self):
        """Test mise à jour partielle de quelques champs"""
        # Créer utilisateur avec toutes les données
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St',
            phone_number='0123456789'
        )
        
        # Mettre à jour seulement nom et adresse
        updated_user = self.user_service.update_user(
            user.id,
            first_name='Johnny',
            address='456 Oak Ave'
        )
        
        self.assertEqual(updated_user.first_name, 'Johnny')
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        self.assertEqual(updated_user.address, '456 Oak Ave')
        self.assertEqual(updated_user.phone_number, '0123456789')  # Inchangé

    def test_update_user_set_address_to_none(self):
        """Test mise à jour pour supprimer l'adresse (None)"""
        # Créer utilisateur avec adresse
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St',
            phone_number=None
        )
        
        # Supprimer l'adresse
        updated_user = self.user_service.update_user(user.id, address=None)
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertIsNone(updated_user.address)

    def test_update_user_set_phone_to_none(self):
        """Test mise à jour pour supprimer le téléphone (None)"""
        # Créer utilisateur avec téléphone
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address=None,
            phone_number='0123456789'
        )
        
        # Supprimer le téléphone
        updated_user = self.user_service.update_user(user.id, phone_number=None)
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertIsNone(updated_user.phone_number)

    def test_update_user_add_address_and_phone(self):
        """Test ajout d'adresse et téléphone à un utilisateur qui n'en avait pas"""
        # Créer utilisateur sans adresse ni téléphone
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Ajouter adresse et téléphone
        updated_user = self.user_service.update_user(
            user.id,
            address='123 New St',
            phone_number='0123456789'
        )
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.address, '123 New St')
        self.assertEqual(updated_user.phone_number, '0123456789')

    def test_update_user_not_found(self):
        """Test mise à jour utilisateur inexistant"""
        with self.assertRaises(ValueError) as context:
            self.user_service.update_user('nonexistent-id', first_name='John')
        
        self.assertIn('user_id', str(context.exception).lower())

    def test_update_user_invalid_email(self):
        """Test mise à jour avec email invalide"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Tenter mise à jour avec email invalide
        with self.assertRaises(ValueError):
            self.user_service.update_user(user.id, email='invalid-email')

    def test_update_user_duplicate_email(self):
        """Test mise à jour avec email déjà utilisé"""
        # Créer deux utilisateurs
        user1 = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        user2 = self.user_service.create_user(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            password='Password456!'
        )
        
        # Tenter de donner à user2 l'email de user1
        with self.assertRaises(ValueError) as context:
            self.user_service.update_user(user2.id, email='john@example.com')
        
        self.assertIn('Email already exists', str(context.exception))

    def test_update_user_with_no_data_raises_error(self):
        """Test qu'une erreur est levée si aucune donnée n'est fournie pour la mise à jour"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )

        # Tenter de mettre à jour sans fournir de données
        with self.assertRaises(ValueError) as context:
            self.user_service.update_user(user.id)

        self.assertIn("No data provided for update", str(context.exception))

    def test_delete_user_existing(self):
        """Test suppression utilisateur existant"""
        # Créer utilisateur
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Supprimer
        result = self.user_service.delete_user(user.id)
        
        self.assertTrue(result)
        
        # Vérifier suppression
        with self.assertRaises(ValueError):
            self.user_service.get_user_by_id(user.id)

    def test_delete_user_not_found(self):
        """Test suppression utilisateur inexistant"""
        with self.assertRaises(ValueError) as context:
            self.user_service.delete_user('nonexistent-id')
        
        self.assertIn('user_id', str(context.exception).lower())

    # Tests de mock supprimés car ils ne correspondent pas à l'architecture actuelle
    # du UserService qui fait ses propres vérifications avant d'appeler le repository


if __name__ == '__main__':
    unittest.main()
