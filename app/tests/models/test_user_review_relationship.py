import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.models.review import Review
from app.models.appointment import Appointment
from app.models.prestation import Prestation


class TestUserReviewRelations(BaseTest):
    def setUp(self):
        super().setUp()
        self.user = User(first_name="John", last_name="Doe",
                         email="john@example.com", 
                         password="Password123!", is_admin=False)
        self.user2 = User(first_name="Jane", last_name="Smith",
                         email="jane@example.com", 
                         password="Password123!", is_admin=False)
        self.prestation = Prestation(name="Massage thérapeutique")
        self.save_to_db(self.user, self.user2, self.prestation)

    def test_user_can_create_review(self):
        # Un utilisateur peut créer un avis
        review = Review(text="Excellent service!", rating=5, user=self.user, prestation=self.prestation)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review._user_id, self.user.id)

    def test_user_multiple_reviews(self):
        # Un utilisateur peut avoir plusieurs avis
        review1 = Review(text="Great massage!", rating=5, user=self.user, prestation=self.prestation)
        review2 = Review(text="Good reflexology session", rating=4, user=self.user, prestation=self.prestation)
        
        self.assertEqual(review1.user, self.user)
        self.assertEqual(review2.user, self.user)
        self.assertNotEqual(review1.id, review2.id)

    def test_review_belongs_to_one_user(self):
        # Un avis appartient à un seul utilisateur
        review = Review(text="Nice service", rating=4, user=self.user, prestation=self.prestation)
        
        # Changer d'utilisateur
        review.user = self.user2
        self.assertEqual(review.user, self.user2)
        self.assertEqual(review._user_id, self.user2.id)

    def test_different_users_different_reviews(self):
        # Différents utilisateurs peuvent laisser des avis
        review1 = Review(text="Amazing experience", rating=5, user=self.user, prestation=self.prestation)
        review2 = Review(text="Very relaxing", rating=4, user=self.user2, prestation=self.prestation)
        
        self.assertEqual(review1.user, self.user)
        self.assertEqual(review2.user, self.user2)
        self.assertNotEqual(review1._user_id, review2._user_id)

    def test_back_populates_user_reviews(self):
    # Testez si l'ajout d'un avis à la liste de l'utilisateur met à jour la relation inverse
        review = Review(text="Test back_populates", rating=5, user=self.user, prestation=self.prestation)
        self.save_to_db(review)
        self.assertIn(review, self.user.reviews)
        self.assertEqual(review.user, self.user)

    # Testez la même chose pour les rendez-vous
        appointment = Appointment(subject="Test back_populates", message="Test", user=self.user, prestation=self.prestation)
        self.save_to_db(appointment)
        self.assertIn(appointment, self.user.appointments)
        self.assertEqual(appointment.user, self.user)


if __name__ == "__main__":
    unittest.main()
