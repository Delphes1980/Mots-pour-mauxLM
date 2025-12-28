#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from app.utils import (
    type_validation, strlen_validation, rating_validation,
    name_validation, email_validation, validate_password,
    hash_password, verify_password, validate_phone_number,
    sanitize_input, generate_temp_password
)


class TestUtilsUnit(unittest.TestCase):
    """Tests unitaires purs pour les fonctions utilitaires"""

    def test_type_validation_success(self):
        """Test validation de type réussie"""
        # Ne lève pas d'exception
        type_validation("test", "string", str)
        type_validation(123, "number", int)
        type_validation(True, "boolean", bool)

    def test_type_validation_failure(self):
        """Test validation de type échouée"""
        with self.assertRaises(TypeError):
            type_validation("test", "number", int)
        
        with self.assertRaises(TypeError):
            type_validation(123, "string", str)

    def test_strlen_validation_success(self):
        """Test validation de longueur réussie"""
        # Ne lève pas d'exception
        strlen_validation("test", "string", 1, 10)
        strlen_validation("a", "string", 1, 1)

    def test_strlen_validation_failure(self):
        """Test validation de longueur échouée"""
        with self.assertRaises(ValueError):
            strlen_validation("", "string", 1, 10)
        
        with self.assertRaises(ValueError):
            strlen_validation("toolongstring", "string", 1, 5)

    def test_rating_validation_success(self):
        """Test validation rating réussie"""
        for rating in [1, 2, 3, 4, 5]:
            result = rating_validation(rating)
            self.assertEqual(result, rating)

    def test_rating_validation_failure(self):
        """Test validation rating échouée"""
        with self.assertRaises(ValueError):
            rating_validation(None)
        
        with self.assertRaises(ValueError):
            rating_validation(0)
        
        with self.assertRaises(ValueError):
            rating_validation(6)

    def test_name_validation_success(self):
        """Test validation nom réussie"""
        valid_names = ["Jean", "Marie-Claire", "O'Connor"]
        for name in valid_names:
            result = name_validation(name, "name")
            self.assertIsInstance(result, str)

    def test_name_validation_failure(self):
        """Test validation nom échouée"""
        with self.assertRaises(ValueError):
            name_validation(None, "name")
        
        with self.assertRaises(ValueError):
            name_validation("Jean123", "name")

    @patch('app.utils.validate_email')
    def test_email_validation_success(self, mock_validate_email):
        """Test validation email réussie"""
        mock_validate_email.return_value = True
        
        result = email_validation('test@example.com')
        self.assertEqual(result, 'test@example.com')

    @patch('app.utils.validate_email')
    def test_email_validation_failure(self, mock_validate_email):
        """Test validation email échouée"""
        mock_validate_email.return_value = False
        
        with self.assertRaises(ValueError):
            email_validation('invalid-email')

    def test_validate_password_success(self):
        """Test validation mot de passe réussie"""
        password = "Password123!"
        result = validate_password(password)
        self.assertEqual(result, password)

    def test_validate_password_failure(self):
        """Test validation mot de passe échouée"""
        with self.assertRaises(ValueError):
            validate_password("short")
        
        with self.assertRaises(ValueError):
            validate_password("nouppercase123!")

    @patch('app.utils.bcrypt')
    def test_hash_password(self, mock_bcrypt):
        """Test hachage mot de passe"""
        mock_bcrypt.generate_password_hash.return_value.decode.return_value = 'hashed'
        
        result = hash_password('password')
        self.assertEqual(result, 'hashed')

    @patch('app.utils.bcrypt')
    def test_verify_password(self, mock_bcrypt):
        """Test vérification mot de passe"""
        mock_bcrypt.check_password_hash.return_value = True
        
        result = verify_password('hashed', 'plain')
        self.assertTrue(result)

    def test_validate_phone_number_success(self):
        """Test validation téléphone réussie"""
        valid_phones = ["+33123456789", "01.23.45.67.89", None]
        for phone in valid_phones:
            result = validate_phone_number(phone)
            if phone is None:
                self.assertIsNone(result)
            else:
                self.assertEqual(result, phone)

    def test_validate_phone_number_failure(self):
        """Test validation téléphone échouée"""
        with self.assertRaises(ValueError):
            validate_phone_number("123")  # Trop court

    @patch('app.utils.bleach')
    def test_sanitize_input_success(self, mock_bleach):
        """Test sanitisation réussie"""
        mock_bleach.clean.return_value = 'clean text'
        
        result = sanitize_input('dirty text', 'field')
        self.assertEqual(result, 'clean text')

    @patch('app.utils.secrets')
    @patch('app.utils.validate_password')
    def test_generate_temp_password(self, mock_validate_password, mock_secrets):
        """Test génération mot de passe temporaire"""
        mock_secrets.choice.side_effect = list('Password123!')
        mock_validate_password.return_value = 'Password123!'
        
        result = generate_temp_password(12)
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()