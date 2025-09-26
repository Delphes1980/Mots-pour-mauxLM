
import unittest
from datetime import datetime
from app.tests.base_test import BaseTest
from app.models.review import Review
from app.models.user import User
from app.models.prestation import Prestation


class TestReview(BaseTest):
    def setUp(self):
        super().setUp()
        self.user = User(first_name="John", last_name="Doe",
                         email="john@example.com", 
                         password="Password123!", is_admin=False)
        self.user2 = User(first_name="Jane", last_name="Doe",
                         email="jane2@example.com", 
                         password="Password123!", is_admin=False)
        self.user3 = User(first_name="Jim", last_name="Doe",
                         email="jim@example.com", 
                         password="Password123!", is_admin=False)
        self.owner = User(first_name="Jane", last_name="McDonald",
                          email="jane.mcdonald@example.com", 
                          password="Password123!")
        self.prestation = Prestation(name="Massage thérapeutique")
        self.save_to_db(self.user, self.user2, self.user3, self.owner, self.prestation)
        self.valid_data = {
            'text': 'Great place!',
            'rating': 5,
            'user': self.user,
            'prestation': self.prestation
        }

    def test_review_creation_valid(self):
        review = Review(**self.valid_data)
        self.assertEqual(review.text, self.valid_data['text'])
        self.assertEqual(review.rating, self.valid_data['rating'])
        self.assertEqual(review.user, self.user)

    def test_missing_required_fields(self):
        with self.assertRaises(ValueError):
            Review(text=None, rating=5, user=self.user, prestation=self.prestation)
        with self.assertRaises(ValueError):
            Review(text='Nice', rating=None, user=self.user, prestation=self.prestation)
        with self.assertRaises(ValueError):
            Review(text='Nice', rating=5, user=None, prestation=self.prestation)

    def test_invalid_text_type_and_length(self):
        with self.assertRaises(ValueError):
            Review(text='', rating=5, user=self.user, prestation=self.prestation)
        with self.assertRaises(TypeError):
            Review(text=123, rating=5, user=self.user, prestation=self.prestation)
        with self.assertRaises(ValueError):
            Review(text='A', rating=5, user=self.user, prestation=self.prestation)
        with self.assertRaises(ValueError):
            Review(text='A'*501, rating=5, user=self.user, prestation=self.prestation)

    def test_invalid_rating_type_and_range(self):
        with self.assertRaises(TypeError):
            Review(text='Nice', rating='bad', user=self.user, prestation=self.prestation)
        with self.assertRaises(ValueError):
            Review(text='Nice', rating=0, user=self.user, prestation=self.prestation)
        with self.assertRaises(ValueError):
            Review(text='Nice', rating=6, user=self.user, prestation=self.prestation)

    def test_rating_boundaries(self):
        # Test limites valides
        review1 = Review(text="Good", rating=1, user=self.user, prestation=self.prestation)
        review5 = Review(text="Excellent", rating=5, user=self.user2, prestation=self.prestation)
        self.assertEqual(review1.rating, 1)
        self.assertEqual(review5.rating, 5)

    def test_property_setters(self):
        review = Review(**self.valid_data)
        review.text = "Updated text"
        review.rating = 4
        self.assertEqual(review.text, "Updated text")
        self.assertEqual(review.rating, 4)

    def test_invalid_user_type(self):
        with self.assertRaises(TypeError):
            Review(text="Nice", rating=5, user="not_a_user", prestation=self.prestation)

    def test_inherited_attributes(self):
        review = Review(**self.valid_data)
        self.assertIsInstance(review.id, str)
        self.assertIsInstance(review.created_at, datetime)
        self.assertIsInstance(review.updated_at, datetime)

    def test_text_whitespace_handling(self):
        review = Review(text="  Great place!  ", rating=5, user=self.user, prestation=self.prestation)
        self.assertEqual(review.text, "Great place!")

    def test_user_assignment(self):
        review = Review(text="Nice place", rating=4, user=self.user, prestation=self.prestation)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review._user_id, self.user.id)
        
        # Test changing user
        review.user = self.user2
        self.assertEqual(review.user, self.user2)
        self.assertEqual(review._user_id, self.user2.id)

    def test_multiple_reviews_same_user(self):
        # Un même utilisateur peut laisser plusieurs avis pour différentes prestations
        review1 = Review(text="Excellent massage therapy session", rating=5, user=self.user, prestation=self.prestation)
        review2 = Review(text="Great reflexology treatment", rating=4, user=self.user, prestation=self.prestation)
        review3 = Review(text="Amazing aromatherapy experience", rating=5, user=self.user, prestation=self.prestation)
        
        # Vérifier que tous les avis sont créés avec le même utilisateur
        self.assertEqual(review1.user, self.user)
        self.assertEqual(review2.user, self.user)
        self.assertEqual(review3.user, self.user)
        
        # Vérifier que les avis ont des contenus différents
        self.assertNotEqual(review1.text, review2.text)
        self.assertNotEqual(review2.text, review3.text)
        
        # Vérifier que les avis ont des IDs uniques
        self.assertNotEqual(review1.id, review2.id)
        self.assertNotEqual(review2.id, review3.id)


if __name__ == "__main__":
    unittest.main()
