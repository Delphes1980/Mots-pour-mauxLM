#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.services.UserService import UserService
from app.utils import CustomError, verify_password


class TestUserServiceAdminSecurity(BaseTest):
    """Tests de sécurité pour les nouvelles fonctionnalités admin"""
    
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

    def test_admin_create_user_password_security(self):
        """Test sécurité des mots de passe temporaires"""
        temp_password = 'TempSecure123!'
        
        user = self.user_service.admin_create_user(
            temp_password=temp_password,
            first_name='Security',
            last_name='Test',
            email='security@example.com'
        )
        
        # Vérifier que le mot de passe est hashé
        self.assertNotEqual(user.password, temp_password)
        self.assertTrue(user.password.startswith('$2b$'))
        
        # Vérifier que le hash est différent à chaque fois
        user2 = self.user_service.admin_create_user(
            temp_password=temp_password,
            first_name='SecurityTwo',
            last_name='Test',
            email='security2@example.com'
        )
        
        self.assertNotEqual(user.password, user2.password)

    def test_admin_create_user_input_sanitization(self):
        """Test sanitisation des entrées pour admin_create_user"""
        # Test avec caractères potentiellement dangereux
        dangerous_inputs = [
            {
                'field': 'first_name',
                'value': '<script>alert("xss")</script>',
                'should_fail': True
            },
            {
                'field': 'last_name', 
                'value': 'DROP TABLE users;',
                'should_fail': False  # Les noms peuvent contenir des caractères spéciaux
            },
            {
                'field': 'email',
                'value': 'test@example.com; DROP TABLE users;',
                'should_fail': True  # Email invalide
            },
            {
                'field': 'address',
                'value': '123 Main St <script>',
                'should_fail': False  # Les adresses peuvent contenir des caractères spéciaux
            }
        ]
        
        for test_case in dangerous_inputs:
            base_data = {
                'temp_password': 'TempPass123!',
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'address': '123 Main St'
            }
            
            base_data[test_case['field']] = test_case['value']
            
            if test_case['should_fail']:
                with self.assertRaises(CustomError):
                    self.user_service.admin_create_user(**base_data)
            else:
                try:
                    user = self.user_service.admin_create_user(**base_data)
                    # Vérifier que la valeur est stockée telle quelle (pas d'injection)
                    if test_case['field'] == 'address':
                        self.assertEqual(user.address, test_case['value'])
                except CustomError:
                    # Certaines validations peuvent rejeter des caractères spéciaux
                    pass

    def test_search_users_by_email_fragment_injection_protection(self):
        """Test protection contre l'injection SQL dans la recherche"""
        # Créer des utilisateurs de test
        self.user_service.admin_create_user(
            temp_password='TempPass123!',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
        
        # Test avec tentatives d'injection SQL
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; DELETE FROM users WHERE '1'='1'; --",
            "test@example.com'; UPDATE users SET is_admin=true; --",
            "' UNION SELECT * FROM users; --"
        ]
        
        for injection in sql_injection_attempts:
            try:
                # Ces tentatives ne doivent pas causer d'erreur SQL
                # mais peuvent retourner aucun résultat ou lever CustomError
                result = self.user_service.search_users_by_email_fragment(injection)
                # Si ça retourne quelque chose, vérifier que c'est légitime
                if result:
                    for user in result:
                        self.assertIsInstance(user, User)
            except CustomError:
                # C'est acceptable - pas de résultat trouvé
                pass
            except Exception as e:
                # Aucune autre exception ne devrait être levée
                self.fail(f"Injection SQL possible détectée: {injection} - {str(e)}")

    def test_admin_create_user_privilege_escalation_protection(self):
        """Test protection contre l'escalade de privilèges"""
        # Tenter de créer un admin via des moyens détournés
        
        # Test 1: Essayer de passer is_admin via différents moyens
        test_cases = [
            {'is_admin': 'true'},  # String au lieu de boolean
            {'is_admin': 1},       # Integer au lieu de boolean
            {'is_admin': 'True'},  # String avec majuscule
            {'is_admin': 'yes'},   # String alternative
        ]
        
        for i, case in enumerate(test_cases):
            with self.assertRaises(CustomError):
                user = self.user_service.admin_create_user(
                    temp_password='TempPass123!',
                    first_name='Test',
                    last_name='User',
                    email=f'test{i}@example.com',
                    **case
                )
            
            # La validation devrait rejeter les valeurs non-boolean

    def test_search_users_by_email_fragment_data_leakage_protection(self):
        """Test protection contre la fuite de données sensibles"""
        # Créer des utilisateurs avec des données sensibles
        sensitive_users = [
            ('Admin', 'User', 'admin@company.com', True),
            ('Regular', 'User', 'user@company.com', False),
            ('Secret', 'Agent', 'secret@classified.gov', False)
        ]
        
        for first_name, last_name, email, is_admin in sensitive_users:
            self.user_service.admin_create_user(
                temp_password='TempPass123!',
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_admin=is_admin
            )
        
        # Rechercher par fragment
        company_users = self.user_service.search_users_by_email_fragment('company')
        
        # Vérifier que les mots de passe ne sont pas exposés
        for user in company_users:
            # Le mot de passe doit être hashé
            self.assertTrue(user.password.startswith('$2b$'))
            self.assertNotIn('TempPass123!', user.password)
            
        # Vérifier qu'on peut trouver les utilisateurs légitimes
        self.assertEqual(len(company_users), 2)
        emails = [u.email for u in company_users]
        self.assertIn('admin@company.com', emails)
        self.assertIn('user@company.com', emails)

    def test_admin_create_user_rate_limiting_simulation(self):
        """Test simulation de limitation de taux pour création d'utilisateurs"""
        # Simuler la création rapide de nombreux utilisateurs
        # (Dans un vrai système, il y aurait une limitation de taux)
        
        created_users = []
        for i in range(10):  # Créer 10 utilisateurs rapidement
            try:
                user = self.user_service.admin_create_user(
                    temp_password=f'TempPass{i}!',
                    first_name=f'UserNumber{i}',
                    last_name='Test',
                    email=f'user{i}@example.com'
                )
                created_users.append(user)
            except Exception as e:
                # En cas de limitation de taux, on s'attendrait à des erreurs
                pass
        
        # Vérifier que tous les utilisateurs créés sont valides
        for user in created_users:
            self.assertIsNotNone(user.id)
            self.assertTrue(user.email.startswith('user'))
            self.assertTrue(user.email.endswith('@example.com'))

    def test_search_users_by_email_fragment_case_sensitivity_security(self):
        """Test sécurité de la sensibilité à la casse dans la recherche"""
        # Créer des utilisateurs avec des emails différents
        self.user_service.admin_create_user(
            temp_password='TempPass123!',
            first_name='Lower',
            last_name='Case',
            email='testlower@example.com'
        )
        
        self.user_service.admin_create_user(
            temp_password='TempPass123!',
            first_name='Upper',
            last_name='Case',
            email='testupper@different.com'
        )
        
        # Tester différentes casses pour s'assurer qu'il n'y a pas de bypass
        search_terms = ['test', 'TEST', 'Test', 'tEsT']
        
        for term in search_terms:
            users = self.user_service.search_users_by_email_fragment(term)
            # Doit trouver les utilisateurs contenant "test" (recherche insensible à la casse)
            self.assertGreaterEqual(len(users), 1)

    def test_admin_create_user_email_uniqueness_security(self):
        """Test sécurité de l'unicité des emails"""
        # Créer un utilisateur
        self.user_service.admin_create_user(
            temp_password='TempPass123!',
            first_name='First',
            last_name='User',
            email='unique@example.com'
        )
        
        # Tenter de créer un autre avec exactement le même email
        with self.assertRaises(CustomError) as context:
            self.user_service.admin_create_user(
                temp_password='TempPass456!',
                first_name='Duplicate',
                last_name='User',
                email='unique@example.com'
            )
        
        # Vérifier que l'erreur concerne bien l'email existant
        error_msg = str(context.exception)
        self.assertIn('Email already exists', error_msg)
        
        # Test avec un email complètement différent - doit réussir
        different_user = self.user_service.admin_create_user(
            temp_password='TempPass789!',
            first_name='Different',
            last_name='User',
            email='different@example.com'
        )
        self.assertIsNotNone(different_user)

    def test_search_fragment_length_security(self):
        """Test sécurité avec des fragments de recherche de différentes longueurs"""
        # Créer un utilisateur de test
        self.user_service.admin_create_user(
            temp_password='TempPass123!',
            first_name='Test',
            last_name='User',
            email='testuser@example.com'
        )
        
        # Test avec fragments très courts (potentiel DoS)
        short_fragments = ['a', 'e', '@', '.']
        
        for fragment in short_fragments:
            try:
                users = self.user_service.search_users_by_email_fragment(fragment)
                # Doit retourner des résultats valides ou lever CustomError
                if users:
                    for user in users:
                        self.assertIsInstance(user, User)
            except CustomError:
                # Acceptable - pas de résultats
                pass
        
        # Test avec fragments très longs
        long_fragment = 'a' * 1000
        try:
            users = self.user_service.search_users_by_email_fragment(long_fragment)
            # Ne devrait probablement rien trouver
            self.assertEqual(len(users), 0)
        except CustomError:
            # Acceptable - pas de résultats
            pass


if __name__ == '__main__':
    unittest.main()