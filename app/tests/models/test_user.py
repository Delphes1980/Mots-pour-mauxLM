from app.models.user import User
from datetime import datetime
import unittest


class TestUser(unittest.TestCase):

    def test_user_creation(self):
        user = User(first_name="John", last_name="Doe",
                    email="john.doe@example.com", password="Password123!")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "john.doe@example.com")
        self.assertFalse(user.is_admin)  # Default value
        self.assertIsInstance(user.id, str)
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsInstance(user.updated_at, datetime)

    def test_admin_user_creation(self):
        user = User("Alice", "Smith", "alice@example.com",
                    password="Password123!", is_admin=True)
        self.assertTrue(user.is_admin)
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Smith")
        self.assertEqual(user.email, "alice@example.com")
        self.assertIsInstance(user.id, str)
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsInstance(user.updated_at, datetime)

    def test_empty_string_first_name(self):
        with self.assertRaises(ValueError) as e:
            User("", "Doe", "john.doe@example.com",
                 password="password")
        self.assertIn("Invalid first_name", str(e.exception))

    def test_long_first_name(self):
        with self.assertRaises(ValueError) as e:
            User("JohnDuudly do whatever somethin tsknslkslkskind kdi",
                 "Doe", "email@email.com", password="password")
        self.assertIn("Invalid first_name", str(e.exception))

    def test_name_not_a_string(self):
        with self.assertRaises(TypeError) as e:
            User(23, "Doe", "email@email.com", password="password")
        self.assertIn("Invalid first_name", str(e.exception))

    def test_name_None(self):
        with self.assertRaises(ValueError) as e:
            User(None, "Doe", "email@email.com", password="password")
        self.assertIn("first_name", str(e.exception))

    def test_missing_last_name(self):
        with self.assertRaises(ValueError) as e:
            User("John", "", "john.doe@example.com", password="password")
        self.assertIn("Invalid last_name", str(e.exception))

    def test_empty_string_last_name(self):
        with self.assertRaises(ValueError) as e:
            User("John", "", "john.doe@example.com", password="password")
        self.assertIn("Invalid last_name", str(e.exception))

    def test_long_last_name_but_ok(self):
        user = User("John", "JohnDuudly do whatever somethin tkind",
                    "email@email.com", password="Password123!")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "JohnDuudly do whatever somethin tkind")
        self.assertEqual(user.email, "email@email.com")
        self.assertIsInstance(user.id, str)
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsInstance(user.updated_at, datetime)

    def test_last_name_not_a_string(self):
        with self.assertRaises(TypeError) as e:
            User("John", 42, "email@email.com", password="password")
        self.assertIn("Invalid last_name", str(e.exception))

    def test_last_name_None(self):
        with self.assertRaises(ValueError) as e:
            User("Jon", None, "email@email.com", password="password")
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
            user = User(first_name=name, last_name="Doe",
                        email="test@example.com", password="Password123!")
            self.assertEqual(user.first_name, name)
            user = User(first_name="John", last_name=name,
                        email="test@example.com", password="Password123!")
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
                User(first_name=name, last_name="Doe",
                     email="test@example.com", password="Password123!")
            with self.assertRaises(ValueError):
                User(first_name="John", last_name=name,
                     email="test@example.com", password="Password123!")

    def test_user_creation_bad_email(self):
        with self.assertRaises(ValueError) as cm:
            User(first_name="Jane", last_name="Doe",
                 email="invalid-email", password="password")
        self.assertIn("Invalid email", str(cm.exception))

    def test_invalid_email_no_at(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "johndoeexample.com",
                 password="password")
        self.assertIn("Invalid email", str(e.exception))

    def test_invalid_email_empty(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "", password="password")
        self.assertIn("Invalid email", str(e.exception))

    def test_invalid_email_None(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", None, password="password")
        self.assertIn("email", str(e.exception))

    # Test de mots de passe
    def test_password_too_short(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "john@example.com", "1234567")  # < 8 chars
        self.assertIn("at least 8 characters", str(e.exception))

    def test_password_no_digit(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "john@example.com", "Password!")
        self.assertIn("at least one digit", str(e.exception))

    def test_password_no_special_char(self):
        with self.assertRaises(ValueError) as e:
            User("John", "Doe", "john@example.com", "Password123")
        self.assertIn("special character", str(e.exception))

    def test_valid_password(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        self.assertIsNotNone(user.password)

    # Tests de hachage et vérification du mot de passe
    def test_password_is_hashed(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        self.assertNotEqual(user.password, "Password123!")

    def test_verify_password(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        self.assertTrue(user.verify_password("Password123!"))
        self.assertFalse(user.verify_password("wrongpassword"))

    # Tests des propriétés hybrides
    def test_property_setters(self):
        user = User("John", "Doe", "john@example.com", "Password123!")
        user.first_name = "Jane"
        user.email = "jane@example.com"
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.email, "jane@example.com")


if __name__ == "__main__":
    unittest.main()
