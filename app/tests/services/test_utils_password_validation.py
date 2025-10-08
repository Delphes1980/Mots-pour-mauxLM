#!/usr/bin/env python3

import unittest
from app.utils import validate_password, hash_password, verify_password, generate_temp_password


class TestPasswordValidation(unittest.TestCase):
    """Tests pour la validation des mots de passe avec nouvelles exigences"""

    def test_validate_password_success(self):
        """Test validation réussie avec mots de passe valides"""
        valid_passwords = [
            "Password123!",
            "MySecure456@",
            "Complex789#Pass",
            "Minimum8!",  # Exactement 8 caractères
            "VeryLongPasswordWithAllRequirements123!@#",
            "Test123$",
            "Secure456%",
            "Strong789&",
            "Valid012*",
            "Good345+",
        ]
        
        for password in valid_passwords:
            try:
                result = validate_password(password)
                self.assertEqual(result, password)
            except ValueError as e:
                self.fail(f"Mot de passe '{password}' devrait être valide mais a levé: {str(e)}")

    def test_validate_password_too_short(self):
        """Test validation échoue pour mots de passe trop courts"""
        short_passwords = [
            "Pass1!",    # 6 caractères
            "Test2@",    # 7 caractères
            "A1!",       # 3 caractères
            "",          # Vide
        ]
        
        for password in short_passwords:
            with self.assertRaises(ValueError) as context:
                validate_password(password)
            self.assertIn("at least 8 characters", str(context.exception))

    def test_validate_password_no_digit(self):
        """Test validation échoue sans chiffre"""
        no_digit_passwords = [
            "Password!",
            "NoDigitHere@",
            "OnlyLetters#",
            "TestPassword$",
        ]
        
        for password in no_digit_passwords:
            with self.assertRaises(ValueError) as context:
                validate_password(password)
            self.assertIn("at least one digit", str(context.exception))

    def test_validate_password_no_uppercase(self):
        """Test validation échoue sans majuscule"""
        no_uppercase_passwords = [
            "password123!",
            "lowercase456@",
            "nouppercasehere789#",
            "test123$",
        ]
        
        for password in no_uppercase_passwords:
            with self.assertRaises(ValueError) as context:
                validate_password(password)
            self.assertIn("uppercase", str(context.exception))

    def test_validate_password_no_special_char(self):
        """Test validation échoue sans caractère spécial"""
        no_special_passwords = [
            "Password123",
            "NoSpecialChar456",
            "TestPassword789",
            "Valid012",
        ]
        
        for password in no_special_passwords:
            with self.assertRaises(ValueError) as context:
                validate_password(password)
            self.assertIn("special character", str(context.exception))

    def test_validate_password_multiple_missing_requirements(self):
        """Test validation échoue avec plusieurs exigences manquantes"""
        invalid_passwords = [
            "weak",           # Trop court, pas de majuscule, pas de chiffre, pas de caractère spécial
            "WeakPassword",   # Pas de chiffre, pas de caractère spécial
            "weakpassword123", # Pas de majuscule, pas de caractère spécial
            "WeakPassword123", # Pas de caractère spécial
            "weak123!",       # Trop court, pas de majuscule
        ]
        
        for password in invalid_passwords:
            with self.assertRaises(ValueError):
                validate_password(password)

    def test_validate_password_none(self):
        """Test validation échoue avec None"""
        with self.assertRaises(ValueError) as context:
            validate_password(None)
        self.assertIn("Expected password but received None", str(context.exception))

    def test_validate_password_empty_string(self):
        """Test validation échoue avec chaîne vide"""
        with self.assertRaises(ValueError) as context:
            validate_password("")
        self.assertIn("at least 8 characters", str(context.exception))

    def test_validate_password_special_characters_variety(self):
        """Test validation avec différents caractères spéciaux"""
        special_chars = "!@#$%^&*()_+=-{}[]|\\:;\"<,>/?`~"
        
        for char in special_chars:
            password = f"Password123{char}"
            try:
                result = validate_password(password)
                self.assertEqual(result, password)
            except ValueError as e:
                self.fail(f"Mot de passe avec caractère spécial '{char}' devrait être valide: {str(e)}")

    def test_hash_password_with_valid_passwords(self):
        """Test hachage avec mots de passe valides"""
        valid_passwords = [
            "Password123!",
            "MySecure456@",
            "Complex789#Pass",
        ]
        
        for password in valid_passwords:
            # Valider d'abord
            validated = validate_password(password)
            # Puis hacher
            hashed = hash_password(validated)
            
            # Vérifier le format bcrypt
            self.assertTrue(hashed.startswith('$2b$'))
            self.assertEqual(len(hashed), 60)
            
            # Vérifier que le hash fonctionne
            self.assertTrue(verify_password(hashed, password))

    def test_generate_temp_password_meets_requirements(self):
        """Test que generate_temp_password génère des mots de passe valides"""
        for _ in range(10):  # Tester plusieurs générations
            temp_password = generate_temp_password()
            
            # Le mot de passe généré doit passer la validation
            try:
                validated = validate_password(temp_password)
                self.assertEqual(validated, temp_password)
            except ValueError as e:
                self.fail(f"Mot de passe temporaire généré '{temp_password}' ne respecte pas les exigences: {str(e)}")
            
            # Vérifier les exigences individuellement
            self.assertGreaterEqual(len(temp_password), 8)
            self.assertTrue(any(c.isupper() for c in temp_password))
            self.assertTrue(any(c.islower() for c in temp_password))
            self.assertTrue(any(c.isdigit() for c in temp_password))
            self.assertTrue(any(c in "!@#$%^&*()_+=-{}[]|\\:;\"<,>/?`~" for c in temp_password))

    def test_generate_temp_password_different_lengths(self):
        """Test génération de mots de passe temporaires de différentes longueurs"""
        lengths = [8, 12, 16, 20]
        
        for length in lengths:
            temp_password = generate_temp_password(length=length)
            
            # Vérifier la longueur
            self.assertEqual(len(temp_password), length)
            
            # Vérifier que le mot de passe respecte les exigences
            try:
                validate_password(temp_password)
            except ValueError as e:
                self.fail(f"Mot de passe temporaire de longueur {length} ne respecte pas les exigences: {str(e)}")

    def test_generate_temp_password_uniqueness(self):
        """Test que generate_temp_password génère des mots de passe uniques"""
        passwords = set()
        
        for _ in range(50):  # Générer 50 mots de passe
            temp_password = generate_temp_password()
            passwords.add(temp_password)
        
        # Tous les mots de passe devraient être uniques
        self.assertEqual(len(passwords), 50)

    def test_password_validation_edge_cases(self):
        """Test cas limites de validation"""
        # Exactement 8 caractères avec toutes les exigences
        edge_case_passwords = [
            "Minimum8!",  # Exactement 8 caractères
            "A1!bcdef",   # Minimum avec tous les types
            "Test123@",   # Cas standard minimum
        ]
        
        for password in edge_case_passwords:
            try:
                result = validate_password(password)
                self.assertEqual(result, password)
            except ValueError as e:
                self.fail(f"Mot de passe limite '{password}' devrait être valide: {str(e)}")

    def test_password_validation_unicode_characters(self):
        """Test validation avec caractères Unicode"""
        # Les caractères Unicode ne devraient pas compter comme caractères spéciaux
        unicode_passwords = [
            "Pässwörd123!",  # Avec accents + exigences
            "Test123é!",     # Avec accent + exigences
            "Válid456@",     # Avec accent + exigences
        ]
        
        for password in unicode_passwords:
            try:
                result = validate_password(password)
                self.assertEqual(result, password)
            except ValueError as e:
                self.fail(f"Mot de passe Unicode '{password}' devrait être valide: {str(e)}")





if __name__ == '__main__':
    unittest.main()