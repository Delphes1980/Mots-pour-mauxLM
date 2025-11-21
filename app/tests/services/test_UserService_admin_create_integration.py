#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.services.UserService import UserService
from app.utils import CustomError, verify_password


class TestUserServiceAdminCreateIntegration(BaseTest):
    """Tests d'intégration pour admin_create_user et search_users_by_email_fragment"""
    
    def setUp(self):
        super().setUp()
        self.user_service = UserService()

        # Créer le ghost user nécessaire
        self.ghost_user = self.user_service.create_user(
            first_name='Ghost',
            last_name='User',
            email='deleted@system.local',
            password='Ghost#2025!',
            is_admin=False
        )

    def test_admin_create_user_integration_with_database(self):
        """Test intégration complète admin_create_user avec base de données"""
        temp_password = 'TempIntegration123!'
        
        # Créer utilisateur via admin
        user = self.user_service.admin_create_user(
            temp_password=temp_password,
            first_name='Integration',
            last_name='Test',
            email='integration@example.com',
            address='123 Integration St',
            phone_number='0123456789',
            is_admin=False
        )
        
        # Vérifier création en base
        self.assertIsNotNone(user.id)
        
        # Récupérer depuis la base pour vérifier persistance
        retrieved_user = self.user_service.get_user_by_id(user.id)
        self.assertEqual(retrieved_user.first_name, 'Integration')
        self.assertEqual(retrieved_user.last_name, 'Test')
        self.assertEqual(retrieved_user.email, 'integration@example.com')
        self.assertEqual(retrieved_user.address, '123 Integration St')
        self.assertEqual(retrieved_user.phone_number, '0123456789')
        self.assertFalse(retrieved_user.is_admin)
        
        # Vérifier que le mot de passe temporaire fonctionne
        self.assertTrue(verify_password(retrieved_user.password, temp_password))

    def test_admin_create_multiple_users_integration(self):
        """Test création de plusieurs utilisateurs par admin"""
        users_data = [
            {
                'temp_password': 'TempPass1!',
                'first_name': 'User1',
                'last_name': 'Test',
                'email': 'user1@example.com'
            },
            {
                'temp_password': 'TempPass2!',
                'first_name': 'User2',
                'last_name': 'Test',
                'email': 'user2@example.com'
            },
            {
                'temp_password': 'TempPass3!',
                'first_name': 'User3',
                'last_name': 'Test',
                'email': 'user3@example.com'
            }
        ]
        
        created_users = []
        for data in users_data:
            user = self.user_service.admin_create_user(**data)
            created_users.append(user)
        
        # Vérifier que tous les utilisateurs sont créés
        self.assertEqual(len(created_users), 3)
        
        # Vérifier via get_all_users
        all_users = [
            u for u in self.user_service.get_all_users()
            if u.email != 'deleted@system.local'
        ]
        self.assertEqual(len(all_users), 3)
        
        # Vérifier les mots de passe temporaires
        for i, user in enumerate(created_users):
            expected_password = users_data[i]['temp_password']
            self.assertTrue(verify_password(user.password, expected_password))

    def test_search_users_by_email_fragment_integration(self):
        """Test intégration complète de la recherche par fragment"""
        # Créer des utilisateurs avec différents domaines
        test_users = [
            ('John', 'Doe', 'john.doe@company.com'),
            ('Jane', 'Smith', 'jane.smith@company.com'),
            ('Bob', 'Johnson', 'bob@example.org'),
            ('Alice', 'Brown', 'alice@test.net'),
            ('Charlie', 'Wilson', 'charlie.wilson@company.com')
        ]
        
        for first_name, last_name, email in test_users:
            self.user_service.admin_create_user(
                temp_password='TempPass123!',
                first_name=first_name,
                last_name=last_name,
                email=email
            )
        
        # Test recherche par domaine
        company_users = self.user_service.search_users_by_email_fragment('company.com')
        self.assertEqual(len(company_users), 3)
        
        company_emails = [u.email for u in company_users]
        self.assertIn('john.doe@company.com', company_emails)
        self.assertIn('jane.smith@company.com', company_emails)
        self.assertIn('charlie.wilson@company.com', company_emails)
        
        # Test recherche par nom
        john_users = self.user_service.search_users_by_email_fragment('john')
        self.assertEqual(len(john_users), 1)
        self.assertEqual(john_users[0].email, 'john.doe@company.com')
        
        # Test recherche par extension
        org_users = self.user_service.search_users_by_email_fragment('.org')
        self.assertEqual(len(org_users), 1)
        self.assertEqual(org_users[0].email, 'bob@example.org')

    def test_admin_create_and_search_integration(self):
        """Test intégration entre admin_create_user et search_users_by_email_fragment"""
        # Créer des utilisateurs via admin
        admin_created_users = [
            {
                'temp_password': 'AdminTemp1!',
                'first_name': 'AdminUser1',
                'last_name': 'Test',
                'email': 'admin.user1@test.com'
            },
            {
                'temp_password': 'AdminTemp2!',
                'first_name': 'AdminUser2',
                'last_name': 'Test',
                'email': 'admin.user2@test.com'
            }
        ]
        
        # Créer des utilisateurs normaux
        normal_user = self.user_service.create_user(
            first_name='NormalUser',
            last_name='Test',
            email='normal.user@test.com',
            password='NormalPass123!'
        )
        
        # Créer via admin
        for data in admin_created_users:
            self.user_service.admin_create_user(**data)
        
        # Rechercher tous les utilisateurs test.com
        test_users = self.user_service.search_users_by_email_fragment('test.com')
        self.assertEqual(len(test_users), 3)
        
        # Vérifier que les utilisateurs créés par admin sont trouvés
        test_emails = [u.email for u in test_users]
        self.assertIn('admin.user1@test.com', test_emails)
        self.assertIn('admin.user2@test.com', test_emails)
        self.assertIn('normal.user@test.com', test_emails)
        
        # Rechercher spécifiquement les utilisateurs admin
        admin_users = self.user_service.search_users_by_email_fragment('admin.user')
        self.assertEqual(len(admin_users), 2)

    def test_admin_create_user_with_update_integration(self):
        """Test intégration admin_create_user suivi d'une mise à jour"""
        temp_password = 'InitialTemp123!'
        
        # Créer utilisateur via admin
        user = self.user_service.admin_create_user(
            temp_password=temp_password,
            first_name='Initial',
            last_name='User',
            email='initial@example.com'
        )
        
        # Vérifier mot de passe temporaire
        self.assertTrue(verify_password(user.password, temp_password))
        
        # Mettre à jour le mot de passe
        new_password = 'NewUserPassword456!'
        updated_user = self.user_service.update_user(
            user.id,
            password=new_password
        )
        
        # Vérifier que l'ancien mot de passe ne fonctionne plus
        self.assertFalse(verify_password(updated_user.password, temp_password))
        # Vérifier que le nouveau mot de passe fonctionne
        self.assertTrue(verify_password(updated_user.password, new_password))
        
        # Vérifier que l'utilisateur est toujours trouvable par recherche
        found_users = self.user_service.search_users_by_email_fragment('initial')
        self.assertEqual(len(found_users), 1)
        self.assertEqual(found_users[0].id, user.id)

    def test_admin_create_user_validation_integration(self):
        """Test intégration des validations lors de la création par admin"""
        # Test avec données invalides - doit échouer
        invalid_cases = [
            {
                'temp_password': 'TempPass123!',
                'first_name': '',  # Nom vide
                'last_name': 'Test',
                'email': 'test@example.com'
            },
            {
                'temp_password': 'TempPass123!',
                'first_name': 'Test',
                'last_name': 'Test',
                'email': 'invalid-email'  # Email invalide
            },
            {
                'temp_password': 'TempPass123!',
                'first_name': 'Test',
                'last_name': 'Test',
                'email': 'test@example.com',
                'phone_number': 'invalid-phone'  # Téléphone invalide
            }
        ]
        
        for case in invalid_cases:
            with self.assertRaises(CustomError):
                self.user_service.admin_create_user(**case)
        
        # Vérifier qu'aucun utilisateur invalide n'a été créé
        all_users = [
            u for u in self.user_service.get_all_users()
            if u.email != 'deleted@system.local'
        ]
        self.assertEqual(len(all_users), 0)

    def test_search_fragment_with_special_characters_integration(self):
        """Test recherche par fragment avec caractères spéciaux"""
        # Créer utilisateurs avec caractères spéciaux
        special_users = [
            ('User', 'Plus', 'user+test@example.com'),
            ('User', 'Dot', 'user.test@example.com'),
            ('User', 'Dash', 'user-test@example.com')
        ]
        
        for first_name, last_name, email in special_users:
            self.user_service.admin_create_user(
                temp_password='TempPass123!',
                first_name=first_name,
                last_name=last_name,
                email=email
            )
        
        # Test recherche avec différents fragments
        plus_users = self.user_service.search_users_by_email_fragment('user+')
        self.assertEqual(len(plus_users), 1)
        self.assertEqual(plus_users[0].email, 'user+test@example.com')
        
        dot_users = self.user_service.search_users_by_email_fragment('user.')
        self.assertEqual(len(dot_users), 1)
        self.assertEqual(dot_users[0].email, 'user.test@example.com')
        
        dash_users = self.user_service.search_users_by_email_fragment('user-')
        self.assertEqual(len(dash_users), 1)
        self.assertEqual(dash_users[0].email, 'user-test@example.com')
        
        # Test recherche générale
        all_user_test = self.user_service.search_users_by_email_fragment('user')
        self.assertEqual(len(all_user_test), 3)


if __name__ == '__main__':
    unittest.main()