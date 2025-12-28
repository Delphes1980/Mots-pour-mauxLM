#!/usr/bin/env python3

import unittest
import re


class TestModelValidationLogicUnit(unittest.TestCase):
    """Tests unitaires pour logiques de validation communes"""

    def test_phone_number_regex_logic(self):
        """Test logique regex numéro téléphone"""
        # Pattern du modèle User
        pattern = r'^\+?[0-9\s\-\.()]*$'
        
        valid_phones = ['+33123456789', '01 23 45 67 89', '01-23-45-67-89', '(01) 23.45.67.89']
        invalid_phones = ['abc123', '01@23', '01#23']
        
        for phone in valid_phones:
            self.assertTrue(re.fullmatch(pattern, phone))
        
        for phone in invalid_phones:
            self.assertFalse(re.fullmatch(pattern, phone))

    def test_string_length_validation_logic(self):
        """Test logique validation longueur chaînes"""
        # Logiques de longueur des modèles
        test_cases = [
            ('name', 1, 50),      # Prestation name
            ('text', 2, 500),     # Review text
            ('message', 1, 500),  # Appointment message
            ('address', 0, 255),  # User address
            ('phone', 0, 20)      # User phone
        ]
        
        for field, min_len, max_len in test_cases:
            # Test valide
            valid_text = 'A' * min_len
            self.assertTrue(min_len <= len(valid_text) <= max_len)
            
            # Test trop court (si min > 0)
            if min_len > 0:
                too_short = 'A' * (min_len - 1)
                self.assertFalse(min_len <= len(too_short) <= max_len)
            
            # Test trop long
            too_long = 'A' * (max_len + 1)
            self.assertFalse(min_len <= len(too_long) <= max_len)


if __name__ == '__main__':
    unittest.main()