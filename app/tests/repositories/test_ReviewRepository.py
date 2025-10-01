import unittest
from sqlalchemy.exc import SQLAlchemyError
from app.tests.base_test import BaseTest
from app.models.review import Review
from app.models.user import User
from app.models.prestation import Prestation
from app.persistence.ReviewRepository import ReviewRepository


class TestReviewRepository(BaseTest):
    def setUp(self):
        super().setUp()
        self.review_repo = ReviewRepository()
        # Forcer l'utilisation de l'instance DB de test
        self.review_repo.db = self.db
        
        # Créer des données de test
        self.user = User(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="Password123!",
            address=None,
            phone_number=None
        )
        self.db.session.add(self.user)
        
        self.prestation = Prestation(name="Massage")
        self.db.session.add(self.prestation)
        
        self.db.session.commit()

    def test_create_review_success(self):
        """Test création avis réussie"""
        review = self.review_repo.create(
            text="Excellent service!",
            rating=5,
            user=self.user,
            prestation=self.prestation
        )
        
        self.assertIsNotNone(review.id)
        self.assertEqual(review.text, "Excellent service!")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.user.id, self.user.id)
        self.assertEqual(review.prestation.id, self.prestation.id)

    def test_create_review_invalid_rating(self):
        """Test création avis avec rating invalide"""
        with self.assertRaises(ValueError):
            self.review_repo.create(
                text="Good service",
                rating=6,  # Invalid rating
                user=self.user,
                prestation=self.prestation
            )

    def test_create_review_no_prestation(self):
        """Test création avis sans prestation"""
        with self.assertRaises(ValueError) as context:
            self.review_repo.create(
                text="Good service",
                rating=4,
                user=self.user,
                prestation=None
            )
        
        self.assertIn("La prestation spécifiée n'existe pas", str(context.exception))

    def test_create_review_duplicate(self):
        """Test création avis en double pour même utilisateur/prestation"""
        # Créer premier avis
        self.review_repo.create(
            text="First review",
            rating=4,
            user=self.user,
            prestation=self.prestation
        )
        
        # Tenter de créer un second avis
        with self.assertRaises(ValueError) as context:
            self.review_repo.create(
                text="Second review",
                rating=5,
                user=self.user,
                prestation=self.prestation
            )
        
        self.assertIn("Un commentaire existe déjà pour cette prestation", str(context.exception))

    def test_get_by_user_id(self):
        """Test récupération avis par user_id"""
        # Créer avis
        created_review = self.review_repo.create(
            text="Great service",
            rating=5,
            user=self.user,
            prestation=self.prestation
        )
        
        # Récupérer par user_id
        found_review = self.review_repo.get_by_attribute("_user_id", self.user.id)
        
        self.assertIsNotNone(found_review)
        self.assertEqual(found_review.id, created_review.id)

    def test_get_by_user_id_not_found(self):
        """Test récupération avis par user_id inexistant"""
        review = self.review_repo.get_by_attribute("_user_id", "nonexistent-id")
        self.assertIsNone(review)

    def test_get_by_prestation_id(self):
        """Test récupération avis par prestation_id"""
        # Créer avis
        created_review = self.review_repo.create(
            text="Amazing service",
            rating=5,
            user=self.user,
            prestation=self.prestation
        )
        
        # Récupérer par prestation_id
        review = self.review_repo.get_by_attribute("_prestation_id", self.prestation.id)
        
        self.assertIsNotNone(review)
        self.assertEqual(review.id, created_review.id)

    def test_get_by_prestation_id_multiple_reviews(self):
        """Test récupération multiple avis pour même prestation"""
        # Créer second utilisateur
        user2 = User(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="Password123!",
            address=None,
            phone_number=None
        )
        self.db.session.add(user2)
        self.db.session.commit()
        
        # Créer deux avis pour même prestation
        review1 = self.review_repo.create(
            text="Good service",
            rating=4,
            user=self.user,
            prestation=self.prestation
        )
        
        review2 = self.review_repo.create(
            text="Excellent service",
            rating=5,
            user=user2,
            prestation=self.prestation
        )
        
        # Récupérer un avis par prestation (get_by_attribute retourne le premier)
        review = self.review_repo.get_by_attribute("_prestation_id", self.prestation.id)
        
        self.assertIsNotNone(review)
        # Vérifier que c'est l'un des deux créés
        self.assertIn(review.id, [review1.id, review2.id])

    def test_get_by_user_and_prestation(self):
        """Test récupération avis par utilisateur et prestation"""
        # Créer avis
        created_review = self.review_repo.create(
            text="Perfect service",
            rating=5,
            user=self.user,
            prestation=self.prestation
        )
        
        # Récupérer par user + prestation
        found_review = self.review_repo.get_by_user_and_prestation(
            self.user.id, 
            self.prestation.id
        )
        
        self.assertIsNotNone(found_review)
        self.assertEqual(found_review.id, created_review.id)

    def test_get_by_user_and_prestation_not_found(self):
        """Test récupération avis inexistant par user + prestation"""
        review = self.review_repo.get_by_user_and_prestation(
            "nonexistent-user", 
            "nonexistent-prestation"
        )
        self.assertIsNone(review)

    def test_inheritance_from_base_repository(self):
        """Test que ReviewRepository hérite bien de BaseRepository"""
        # Test méthodes héritées avec create
        review = self.review_repo.create(
            text="Test review",
            rating=4,
            user=self.user,
            prestation=self.prestation
        )
        self.assertIsNotNone(review.id)
        
        # Test get_by_id (méthode héritée)
        found_review = self.review_repo.get_by_id(review.id)
        self.assertEqual(found_review.id, review.id)
        
        # Test get_all (méthode héritée)
        all_reviews = self.review_repo.get_all()
        self.assertIn(review, all_reviews)

    def test_get_all_reviews(self):
        """Test récupération de tous les avis"""
        # Créer second utilisateur
        user2 = User(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="Password123!",
            address=None,
            phone_number=None
        )
        self.db.session.add(user2)
        
        # Créer seconde prestation
        prestation2 = Prestation(name="Thérapie")
        self.db.session.add(prestation2)
        self.db.session.commit()
        
        # Créer plusieurs avis
        review1 = self.review_repo.create(
            text="Excellent service",
            rating=5,
            user=self.user,
            prestation=self.prestation
        )
        review2 = self.review_repo.create(
            text="Très bien",
            rating=4,
            user=user2,
            prestation=prestation2
        )
        
        # Récupérer tous
        all_reviews = self.review_repo.get_all()
        
        self.assertEqual(len(all_reviews), 2)
        review_ids = [r.id for r in all_reviews]
        self.assertIn(review1.id, review_ids)
        self.assertIn(review2.id, review_ids)

    def test_get_all_empty(self):
        """Test get_all() quand aucun avis n'existe"""
        all_reviews = self.review_repo.get_all()
        self.assertEqual(len(all_reviews), 0)

    def test_model_class_consistency(self):
        """Test que model_class est bien configuré"""
        self.assertEqual(self.review_repo.model_class, Review)


if __name__ == "__main__":
    unittest.main()