#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.services.UserService import UserService
from app.utils import CustomError, verify_password


class TestUserServiceSimple(BaseTest):
    """Tests pour UserService sans mocks - utilise la vraie DB"""
    
    def setUp(self):
        super().setUp()
        self.user_service = UserService()

    def test_create_user_success(self):
        """Test création utilisateur réussie"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St',
            phone_number='0123456789'
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'john@example.com')
        self.assertEqual(user.address, '123 Main St')
        self.assertEqual(user.phone_number, '0123456789')
        self.assertFalse(user.is_admin)

    def test_create_user_minimal_data(self):
        """Test création avec données minimales"""
        user = self.user_service.create_user(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            password='Password123!',
            address=None,
            phone_number=None
        )
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Smith')
        self.assertEqual(user.email, 'jane@example.com')
        self.assertIsNone(user.address)
        self.assertIsNone(user.phone_number)
        self.assertFalse(user.is_admin)

    def test_create_user_admin(self):
        """Test création utilisateur admin"""
        user = self.user_service.create_user(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            password='AdminPass123!',
            is_admin=True
        )
        
        self.assertTrue(user.is_admin)

    def test_create_user_duplicate_email(self):
        """Test création avec email existant"""
        # Créer premier utilisateur
        self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Tenter de créer un autre avec même email
        with self.assertRaises(CustomError) as context:
            self.user_service.create_user(
                first_name='Jane',
                last_name='Smith',
                email='john@example.com',
                password='Password456!'
            )
        
        self.assertIn('Email already exists', str(context.exception))

    def test_create_user_invalid_email(self):
        """Test création avec email invalide"""
        with self.assertRaises(CustomError):
            self.user_service.create_user(
                first_name='John',
                last_name='Doe',
                email='invalid-email',
                password='Password123!'
            )

    def test_create_user_invalid_password(self):
        """Test création avec mot de passe invalide"""
        with self.assertRaises(CustomError):
            self.user_service.create_user(
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                password='weak'
            )

    def test_get_user_by_id_existing(self):
        """Test récupération par ID existant"""
        created_user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        found_user = self.user_service.get_user_by_id(created_user.id)
        
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.id, created_user.id)
        self.assertEqual(found_user.email, 'john@example.com')

    def test_get_user_by_id_not_found(self):
        """Test récupération par ID inexistant"""
        with self.assertRaises(CustomError):
            self.user_service.get_user_by_id('nonexistent-id')

    def test_get_user_by_email_existing(self):
        """Test récupération par email existant"""
        created_user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        found_user = self.user_service.get_user_by_email('john@example.com')
        
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.id, created_user.id)
        self.assertEqual(found_user.email, 'john@example.com')

    def test_get_user_by_email_not_found(self):
        """Test récupération par email inexistant"""
        with self.assertRaises(CustomError) as context:
            self.user_service.get_user_by_email('nonexistent@example.com')
        
        self.assertIn('User not found', str(context.exception))

    def test_get_all_users(self):
        """Test récupération de tous les utilisateurs"""
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
        
        all_users = self.user_service.get_all_users()
        
        self.assertEqual(len(all_users), 2)
        user_ids = [u.id for u in all_users]
        self.assertIn(user1.id, user_ids)
        self.assertIn(user2.id, user_ids)

    def test_get_all_users_empty(self):
        """Test get_all_users quand aucun utilisateur"""
        all_users = self.user_service.get_all_users()
        self.assertEqual(len(all_users), 0)

    def test_update_user_single_field(self):
        """Test mise à jour d'un seul champ"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        updated_user = self.user_service.update_user(user.id, first_name='Johnny')
        
        self.assertEqual(updated_user.first_name, 'Johnny')
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé

    def test_update_user_multiple_fields(self):
        """Test mise à jour de plusieurs champs"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St'
        )
        
        updated_user = self.user_service.update_user(
            user.id,
            first_name='Johnny',
            last_name='Smith',
            address='456 Oak Ave'
        )
        
        self.assertEqual(updated_user.first_name, 'Johnny')
        self.assertEqual(updated_user.last_name, 'Smith')
        self.assertEqual(updated_user.address, '456 Oak Ave')
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé

    def test_update_user_password(self):
        """Test mise à jour du mot de passe"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Vérifier ancien mot de passe
        self.assertTrue(verify_password(user.password, 'Password123!'))
        
        # Mettre à jour
        updated_user = self.user_service.update_user(user.id, password='NewPassword456!')
        
        # Vérifier nouveau mot de passe
        self.assertTrue(verify_password(updated_user.password, 'NewPassword456!'))
        self.assertFalse(verify_password(updated_user.password, 'Password123!'))

    def test_update_user_invalid_password(self):
        """Test mise à jour avec mot de passe invalide"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        with self.assertRaises(CustomError):
            self.user_service.update_user(user.id, password='weak')

    def test_update_user_duplicate_email(self):
        """Test mise à jour avec email déjà utilisé"""
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
        
        with self.assertRaises(CustomError) as context:
            self.user_service.update_user(user2.id, email='john@example.com')
        
        self.assertIn('Email already exists', str(context.exception))

    def test_update_user_not_found(self):
        """Test mise à jour utilisateur inexistant"""
        with self.assertRaises(CustomError):
            self.user_service.update_user('nonexistent-id', first_name='John')

    def test_update_user_no_data(self):
        """Test mise à jour sans données"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )

        with self.assertRaises(CustomError) as context:
            self.user_service.update_user(user.id)

        self.assertIn("No data provided for update", str(context.exception))

    def test_delete_user_existing(self):
        """Test suppression utilisateur existant"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        result = self.user_service.delete_user(user.id)
        
        self.assertTrue(result)
        
        # Vérifier suppression
        with self.assertRaises(CustomError):
            self.user_service.get_user_by_id(user.id)

    def test_delete_user_not_found(self):
        """Test suppression utilisateur inexistant"""
        with self.assertRaises(CustomError):
            self.user_service.delete_user('nonexistent-id')

    def test_update_user_first_name_only(self):
        """Test mise à jour du prénom seulement"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St',
            phone_number='0123456789'
        )
        
        updated_user = self.user_service.update_user(user.id, first_name='Johnny')
        
        self.assertEqual(updated_user.first_name, 'Johnny')
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        self.assertEqual(updated_user.address, '123 Main St')  # Inchangé
        self.assertEqual(updated_user.phone_number, '0123456789')  # Inchangé

    def test_update_user_last_name_only(self):
        """Test mise à jour du nom seulement"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        updated_user = self.user_service.update_user(user.id, last_name='Smith')
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Smith')
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé

    def test_update_user_email_only(self):
        """Test mise à jour de l'email seulement"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        updated_user = self.user_service.update_user(user.id, email='john.doe@example.com')
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john.doe@example.com')

    def test_update_user_address_only(self):
        """Test mise à jour de l'adresse seulement"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St'
        )
        
        updated_user = self.user_service.update_user(user.id, address='456 Oak Ave')
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        self.assertEqual(updated_user.address, '456 Oak Ave')

    def test_update_user_phone_number_only(self):
        """Test mise à jour du téléphone seulement"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            phone_number='0123456789'
        )
        
        updated_user = self.user_service.update_user(user.id, phone_number='0987654321')
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        self.assertEqual(updated_user.phone_number, '0987654321')

    def test_update_user_is_admin_only(self):
        """Test mise à jour du statut admin seulement"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        updated_user = self.user_service.update_user(user.id, is_admin=True)
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        self.assertTrue(updated_user.is_admin)

    def test_update_user_password_validation_requirements(self):
        """Test validation des exigences du mot de passe lors mise à jour"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Test mot de passe trop court
        with self.assertRaises(CustomError):
            self.user_service.update_user(user.id, password='Short1!')
        
        # Test mot de passe sans chiffre
        with self.assertRaises(CustomError):
            self.user_service.update_user(user.id, password='NoDigitPassword!')
        
        # Test mot de passe sans caractère spécial
        with self.assertRaises(CustomError):
            self.user_service.update_user(user.id, password='NoSpecialChar123')
        
        # Test mot de passe sans majuscule
        with self.assertRaises(CustomError):
            self.user_service.update_user(user.id, password='nouppercase123!')
        
        # Vérifier que l'ancien mot de passe fonctionne toujours
        self.assertTrue(verify_password(user.password, 'Password123!'))

    def test_update_user_password_with_other_fields(self):
        """Test mise à jour du mot de passe avec d'autres champs"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        updated_user = self.user_service.update_user(
            user.id,
            first_name='Johnny',
            password='SuperSecure456!'
        )
        
        self.assertEqual(updated_user.first_name, 'Johnny')
        self.assertEqual(updated_user.last_name, 'Doe')  # Inchangé
        self.assertEqual(updated_user.email, 'john@example.com')  # Inchangé
        # Vérifier nouveau mot de passe
        self.assertTrue(verify_password(updated_user.password, 'SuperSecure456!'))
        self.assertFalse(verify_password(updated_user.password, 'Password123!'))

    def test_update_user_multiple_fields(self):
        """Test mise à jour de plusieurs champs en même temps"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St',
            phone_number='0123456789'
        )
        
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
        self.assertTrue(verify_password(updated_user.password, 'NewPassword456!'))
        self.assertFalse(verify_password(updated_user.password, 'Password123!'))

    def test_update_user_partial_fields(self):
        """Test mise à jour partielle de quelques champs"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St',
            phone_number='0123456789'
        )
        
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
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            address='123 Main St'
        )
        
        updated_user = self.user_service.update_user(user.id, address=None)
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertIsNone(updated_user.address)

    def test_update_user_set_phone_to_none(self):
        """Test mise à jour pour supprimer le téléphone (None)"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!',
            phone_number='0123456789'
        )
        
        updated_user = self.user_service.update_user(user.id, phone_number=None)
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertIsNone(updated_user.phone_number)

    def test_update_user_add_address_and_phone(self):
        """Test ajout d'adresse et téléphone à un utilisateur qui n'en avait pas"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        updated_user = self.user_service.update_user(
            user.id,
            address='123 New St',
            phone_number='0123456789'
        )
        
        self.assertEqual(updated_user.first_name, 'John')  # Inchangé
        self.assertEqual(updated_user.address, '123 New St')
        self.assertEqual(updated_user.phone_number, '0123456789')

    def test_update_user_invalid_email(self):
        """Test mise à jour avec email invalide"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        with self.assertRaises(CustomError):
            self.user_service.update_user(user.id, email='invalid-email')

    def test_password_hashing(self):
        """Test que les mots de passe sont bien hashés"""
        user = self.user_service.create_user(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            password='Password123!'
        )
        
        # Le mot de passe stocké ne doit pas être en clair
        self.assertNotEqual(user.password, 'Password123!')
        # Doit être un hash bcrypt
        self.assertTrue(user.password.startswith('$2b$'))
        # Doit pouvoir être vérifié
        self.assertTrue(verify_password(user.password, 'Password123!'))


if __name__ == '__main__':
    unittest.main()