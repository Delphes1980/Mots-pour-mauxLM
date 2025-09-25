import unittest
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.user import User
from app.models.appointment import Appointment


class TestPrestationReviewRelations(unittest.TestCase):
    def setUp(self):
        self.user = User(first_name="John", last_name="Doe",
                         email="john@example.com", 
                         password="Password123!", is_admin=False)
        self.user2 = User(first_name="Jane", last_name="Smith",
                         email="jane@example.com", 
                         password="Password456!", is_admin=False)
        self.prestation = Prestation(name="Massage suédois")
        self.prestation2 = Prestation(name="Réflexologie plantaire")

    def test_prestation_can_have_review(self):
        # Une prestation peut avoir un avis
        review = Review(text="Excellent massage!", rating=5, 
                       user=self.user, prestation=self.prestation)
        self.assertEqual(review.prestation, self.prestation)
        self.assertEqual(review._prestation_id, self.prestation.id)

    def test_prestation_multiple_reviews(self):
        # Une prestation peut avoir plusieurs avis
        review1 = Review(text="Très relaxant", rating=5, 
                        user=self.user, prestation=self.prestation)
        review2 = Review(text="Bon massage", rating=4, 
                        user=self.user2, prestation=self.prestation)
        
        self.assertEqual(review1.prestation, self.prestation)
        self.assertEqual(review2.prestation, self.prestation)
        self.assertNotEqual(review1.id, review2.id)

    def test_review_belongs_to_one_prestation(self):
        # Un avis appartient à une seule prestation
        review = Review(text="Service agréable", rating=4, 
                       user=self.user, prestation=self.prestation)
        
        # Changer de prestation
        review.prestation = self.prestation2
        self.assertEqual(review.prestation, self.prestation2)
        self.assertEqual(review._prestation_id, self.prestation2.id)

    def test_different_prestations_different_reviews(self):
        # Différentes prestations peuvent avoir des avis
        review1 = Review(text="Massage suédois parfait", rating=5, 
                        user=self.user, prestation=self.prestation)
        review2 = Review(text="Réflexologie apaisante", rating=4, 
                        user=self.user2, prestation=self.prestation2)
        
        self.assertEqual(review1.prestation, self.prestation)
        self.assertEqual(review2.prestation, self.prestation2)
        self.assertNotEqual(review1._prestation_id, review2._prestation_id)

    def test_prestation_review_rating_variety(self):
        # Une prestation peut avoir des avis avec différentes notes
        ratings_comments = [
            (5, "Parfait, je recommande vivement"),
            (4, "Très bien, quelques améliorations possibles"),
            (3, "Correct, sans plus"),
            (5, "Excellent service, très professionnel")
        ]
        
        reviews = []
        for rating, text in ratings_comments:
            review = Review(text=text, rating=rating, 
                           user=self.user, prestation=self.prestation)
            reviews.append(review)
            self.assertEqual(review.prestation, self.prestation)
        
        # Vérifier l'unicité des avis
        ids = [r.id for r in reviews]
        self.assertEqual(len(ids), len(set(ids)))
        
        # Vérifier la variété des notes
        ratings = [r.rating for r in reviews]
        self.assertIn(5, ratings)
        self.assertIn(4, ratings)
        self.assertIn(3, ratings)

    def test_review_prestation_validation(self):
        # Test validation prestation requise
        with self.assertRaises(ValueError) as context:
            Review(text="Test avis", rating=5, user=self.user, prestation=None)
        self.assertIn("Prestation is required", str(context.exception))

    def test_same_user_different_prestations_reviews(self):
        # Un même utilisateur peut laisser des avis sur différentes prestations
        review1 = Review(text="Massage suédois relaxant", rating=5, 
                        user=self.user, prestation=self.prestation)
        review2 = Review(text="Réflexologie efficace", rating=4, 
                        user=self.user, prestation=self.prestation2)
        
        self.assertEqual(review1.user, self.user)
        self.assertEqual(review2.user, self.user)
        self.assertEqual(review1.prestation, self.prestation)
        self.assertEqual(review2.prestation, self.prestation2)
        self.assertNotEqual(review1.prestation, review2.prestation)


if __name__ == "__main__":
    unittest.main()