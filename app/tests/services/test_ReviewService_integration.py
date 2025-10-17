import unittest
from app.tests.base_test import BaseTest
from app.services.ReviewService import ReviewService
from app.models.user import User
from app.models.prestation import Prestation


class TestReviewServiceIntegration(BaseTest):
    """Tests d'intégration pour ReviewService avec vraie base de données"""

    def setUp(self):
        super().setUp()
        self.service = ReviewService()
        self.service.review_repository.db = self.db
        self.service.user_repository.db = self.db
        self.service.prestation_repository.db = self.db
        
        # Créer des données de test
        self.user = User(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@test.com",
            password="MotDePasse123!",
            is_admin=False
        )
        self.db.session.add(self.user)
        
        self.prestation = Prestation(name="Massage relaxant")
        self.db.session.add(self.prestation)
        self.db.session.commit()

    def test_full_review_lifecycle(self):
        """Test cycle complet : création, lecture, mise à jour, suppression"""
        # Création
        review = self.service.create_review(
            rating=5,
            text="Excellent service",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        self.assertIsNotNone(review.id)
        self.assertEqual(review.rating, 5)
        
        # Lecture
        retrieved_review = self.service.get_review_by_id(review.id)
        self.assertEqual(retrieved_review.text, "Excellent service")
        
        # Mise à jour
        updated_review = self.service.update_review(
            review.id,
            current_user_id=self.user.id,
            rating=4,
            text="Très bien")
        self.assertEqual(updated_review.rating, 4)
        self.assertEqual(updated_review.text, "Très bien")
        
        # Suppression
        result = self.service.delete_review(review.id)
        self.assertTrue(result)
        
        # Vérification suppression
        from app.utils import CustomError
        with self.assertRaises(CustomError):
            self.service.get_review_by_id(review.id)

    def test_business_rule_one_review_per_user_prestation(self):
        """Test règle métier : un seul avis par utilisateur/prestation"""
        # Premier avis
        self.service.create_review(
            rating=5,
            text="Premier avis",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Tentative de second avis
        from app.utils import CustomError
        with self.assertRaises(CustomError) as context:
            self.service.create_review(
                rating=4,
                text="Second avis",
                user_id=self.user.id,
                prestation_id=self.prestation.id
            )
        
        self.assertIn("existe", str(context.exception))

    def test_get_reviews_by_prestation_multiple_users(self):
        """Test récupération avis par prestation avec plusieurs utilisateurs"""
        # Créer second utilisateur
        user2 = User(
            first_name="Marie",
            last_name="Martin",
            email="marie@test.com",
            password="Password123!",
            is_admin=False
        )
        self.db.session.add(user2)
        self.db.session.commit()
        
        # Créer avis pour chaque utilisateur
        review1 = self.service.create_review(
            rating=5, text="Excellent", user_id=self.user.id, prestation_id=self.prestation.id
        )
        review2 = self.service.create_review(
            rating=4, text="Très bien", user_id=user2.id, prestation_id=self.prestation.id
        )
        
        # Récupérer tous les avis pour cette prestation
        reviews = self.service.get_review_by_prestation(self.prestation.id)
        
        self.assertEqual(len(reviews), 2)
        review_ids = [r.id for r in reviews]
        self.assertIn(review1.id, review_ids)
        self.assertIn(review2.id, review_ids)


if __name__ == '__main__':
    unittest.main()