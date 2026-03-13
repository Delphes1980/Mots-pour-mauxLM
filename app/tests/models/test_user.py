from app.models.user import User
from datetime import datetime
import unittest
from app.tests.base_test import BaseTest


class TestUser(BaseTest):

    def test_user_creation(self):
        user = User("John", "Doe", "john.doe@example.com", "Password123!")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "john.doe@example.com")
        self.assertFalse(user.is_admin)  # Default value
        self.assertIsInstance(user.id, str)
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsInstance(user.updated_at, datetime)

    def test_admin_user_creation(self):
        user = User("Alice", "Smith", "alice@example.com", "Password123!", is_admin=True)
        self.assertTrue(user.is_admin)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Smith")
        self.assertEqual(user.email, "alice@example.com")
        self.assertIsInstance(user.id, str)
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsInstance(user.updated_at, datetime)

    def test_empty_string_first_name(self):
        with self.assertRaises(ValueError) as e:
            User("", "Doe", "john.doe@example.com", "Password123!")
        self.assertIn("Invalid first_name", str(e.exception))

    def test_long_first_name(self):
        with self.assertRaises(ValueError) as e:
            User("JohnDuudly do whatever somethin tsknslkslkskind kdi",
                 "Doe", "email@email.com", "Password123!")
        self.assertIn("Invalid first_name", str(e.exception))

    def test_name_not_a_string(self):
        with self.assertRaises(TypeError) as e:
            User(23, "Doe", "email@email.com", "Password123!")
        self.assertIn("Invalid first_name", str(e.exception))

    def test_name_None(self):
        with self.assertRaises(ValueError) as e:
            User(None, "Doe", "email@email.com", "Password123!")
        self.assertIn("first_name", str(e.exception))

    def test_missing_last_name(self):
        with self.assertRaises(ValueError) as e:
            User("John", "", "john.doe@example.com", "Password123!")
        self.assertIn("Invalid last_name", str(e.exception))

    def test_empty_string_last_name(self):
        with self.assertRaises(ValueError) as e:
            User("John", "", "john.doe@example.com", "Password123!")
        self.assertIn("Invalid last_name", str(e.exception))

    def test_long_last_name_but_ok(self):
        user = User("John", "JohnDuudly do whatever somethin tkind",
                    "email@email.com", "Password123!")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "JohnDuudly do whatever somethin tkind")
        self.assertEqual(user.email, "email@email.com")
        self.assertIsInstance(user.id, str)
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsInstance(user.updated_at, datetime)

    def test_last_name_not_a_string(self):
        with self.assertRaises(TypeError) as e:
            User("John", 42, "email@email.com", "Password123!")
        self.assertIn("Invalid last_name", str(e.exception))

    def test_last_name_None(self):
        with self.assertRaises(ValueError) as e:
            User("Jon", None, "email@email.com", "Password123!")
        self.assertIn("last_name", str(e.exception))

    def test_name_with_accents_and_special_characters(self):
        # Acceptable names with accents, dots, apostrophes, and dashes
        valid_names = [
            "José", "François", "Müller", "Çelik", "Łukasz", "Zoë",
            "Dvořák", "O'Connor", "Jean-Pierre", "Ana-Maria",
            "Dvořák-Smith", "Zoë-Marie", "J.R.R.", "J. K.",
            "Smith-Jones", "D'Arcy", "St. John",
            "Pierre Marie de la Rosa"
        ]
        for name in valid_names:
            user = User(name, "Doe", "test@example.com", "Password123!")
            self.assertEqual(user.first_name, name)
            user = User("John", name, "test@example.com", "Password123!")
            self.assertEqual(user.last_name, name)

        # Names with invalid special characters or numbers should
        # raise ValueError
        invalid_names = [
            "J*hn", "Ann3", "M@rie", "Al/ice", "Bob!", "Eve#", "123",
            "Jean--Pierre", "Jean..Pierre", "Jean''Pierre",
            "Jean.-Pierre", "-Jean", ".Jean", "Jean-", "Jean'", "'Jean"
        ]
        for name in invalid_names:
            with self.assertRaises(ValueError):
                User(name, "Doe", "test@example.com", "Password123!")
            with self.assertRaises(ValueError):
                User("John", name, "test@example.com", "Password123!")

    def test_user_creation_bad_email(self):
        with self.assertRaises(ValueError) as cm:
            User("Jane", "Doe", "invalid-email", "Password123!")
        self.assertIn("Adresse e-mail invalide", str(cm.exception))

    def test_invalid_email_no_at(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "johndoeexample.com", "Password123!")
        self.assertIn("Adresse e-mail invalide", str(e.exception))

    def test_invalid_email_empty(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "", "Password123!")
        self.assertIn("Adresse e-mail invalide", str(e.exception))

    def test_invalid_email_None(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", None, "Password123!")
        self.assertIn("Email attendu", str(e.exception))

    # Test de mots de passe
    def test_password_too_short(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "john@example.com", "Pass1!")  # < 12 chars
        self.assertIn("au moins 12 caractères", str(e.exception))

    def test_password_no_digit(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "john@example.com", "Passwordtest!")
        self.assertIn("au moins un chiffre", str(e.exception))

    def test_password_invalid_variations(self):
        """Test différentes variations de mots de passe invalides"""
        invalid_passwords = [
            "weak",  # Trop court, pas de majuscule, pas de caractère spécial
            "WeakPassword",  # Pas de chiffre, pas de caractère spécial
            "weakpassword123",  # Pas de majuscule, pas de caractère spécial
            "WeakPassword123",  # Pas de caractère spécial
            "Weak12!",  # Trop court (7 caractères)
            "password123!",  # Pas de majuscule
            "PASSWORD123!",  # Pas de minuscule
        ]
        
        for password in invalid_passwords:
            with self.assertRaises(ValueError):
                User("John", "Doe", "john@example.com", password)

    def test_password_no_special_char(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "john@example.com", "Password1234")
        self.assertIn("caractère spécial", str(e.exception))

    def test_password_no_uppercase(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "john@example.com", "password123!")
        self.assertIn("lettre majuscule", str(e.exception))

    def test_password_no_lowercase(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "john@example.com", "PASSWORD123!")
        self.assertIn("lettre minuscule", str(e.exception))

    def test_valid_password(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        self.assertIsNotNone(user.password)

    def test_valid_password_variations(self):
        """Test différentes variations de mots de passe valides"""
        valid_passwords = [
            "Password123!",
            "MySecure456@",
            "Complex789#Pass",
            "Password123!",  # Exactement 12 caractères
            "VeryLongPasswordWithAllRequirements123!@#",
        ]
        
        for password in valid_passwords:
            user = User("John", "Doe", "john@example.com", password)
            self.assertIsNotNone(user.password)
            # Vérifier que le mot de passe est hashé
            self.assertNotEqual(user.password, password)

    # Tests de hachage et vérification du mot de passe
    def test_password_is_hashed(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        self.assertNotEqual(user.password, "Password123!")

    def test_verify_password(self):
        from app.utils import verify_password
        user = User("John", "Doe", "john@example.com", "Password123!")
        self.assertTrue(verify_password(user.password, "Password123!"))
        self.assertFalse(verify_password(user.password, "wrongpassword"))

    # Tests des propriétés hybrides
    def test_property_setters(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        user.first_name = "Jane"
        user.email = "jane@example.com"
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.email, "jane@example.com")

    # Tests pour address
    def test_user_with_address(self):
        user = User("John", "Doe", "john@example.com", "Password123!", "123 Main St, Paris")
        self.assertEqual(user.address, "123 Main St, Paris")

    def test_user_without_address(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        self.assertIsNone(user.address)

    def test_address_too_long(self):
        long_address = "A" * 256  # Plus de 255 caractères
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "john@example.com", "Password123!", long_address)
        self.assertIn("Invalid address", str(e.exception))

    def test_address_wrong_type(self):
        with self.assertRaises(TypeError) as e:
            User("John", "Doe", "john@example.com", "Password123!", 123)
        self.assertIn("Invalid address", str(e.exception))

    def test_address_setter(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        user.address = "456 Oak Ave, Lyon"
        self.assertEqual(user.address, "456 Oak Ave, Lyon")
        user.address = None
        self.assertIsNone(user.address)

    # Tests pour phone_number
    def test_user_with_phone_number(self):
        user = User("John", "Doe", "john@example.com", "Password123!", phone_number="0123456789")
        self.assertEqual(user.phone_number, "0123456789")

    def test_user_without_phone_number(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        self.assertIsNone(user.phone_number)

    def test_phone_number_formats(self):
        valid_phones = [
            "0123456789",
            "+33123456789", 
            "01 23 45 67 89",
            "01-23-45-67-89",
            "(01) 23 45 67 89",
            "+33 1 23 45 67 89"
        ]
        for phone in valid_phones:
            user = User("John", "Doe", "john@example.com", "Password123!", phone_number=phone)
            self.assertEqual(user.phone_number, phone)

    def test_phone_number_invalid_format(self):
        invalid_phones = [
            "abc123",
            "123abc", 
            "01/23/45/67/89",
            "01@23456789",
            "01#23456789"
        ]
        for phone in invalid_phones:
            with self.assertRaises(ValueError) as e:
                User("John", "Doe", "john@example.com", "Password123!", phone_number=phone)
            self.assertIn("Invalid phone number", str(e.exception))

    def test_phone_number_too_long(self):
        long_phone = "0" * 21  # Plus de 20 caractères
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "john@example.com", "Password123!", phone_number=long_phone)
        self.assertIn("Invalid phone_number", str(e.exception))

    def test_phone_number_wrong_type(self):
        with self.assertRaises(TypeError) as e:
            User("John", "Doe", "john@example.com", "Password123!", phone_number=123456789)
        self.assertIn("Invalid phone_number", str(e.exception))

    def test_phone_number_setter(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        user.phone_number = "0987654321"
        self.assertEqual(user.phone_number, "0987654321")
        user.phone_number = None
        self.assertIsNone(user.phone_number)

    # Test combinaisons address et phone_number
    def test_user_with_both_address_and_phone(self):
        user = User("John", "Doe", "john@example.com", "Password123!", "123 Main St", "0123456789")
        self.assertEqual(user.address, "123 Main St")
        self.assertEqual(user.phone_number, "0123456789")

    def test_user_with_only_address(self):
        user = User("John", "Doe", "john@example.com", "Password123!", "123 Main St")
        self.assertEqual(user.address, "123 Main St")
        self.assertIsNone(user.phone_number)

    def test_user_with_only_phone(self):
        user = User("John", "Doe", "john@example.com", "Password123!", phone_number="0123456789")
        self.assertIsNone(user.address)
        self.assertEqual(user.phone_number, "0123456789")


if __name__ == "__main__":
    unittest.main()
