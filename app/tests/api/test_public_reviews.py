import unittest
import json
from app.tests.base_test import BaseTest
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.services.ReviewService import ReviewService
from app.services.facade import Facade
from app.api.v1.authentication import api as auth_api
from app.api.v1.reviews import api as reviews_api


class TestPublicReviewsEndToEnd(BaseTest):
    def test_base_is_clean(self):
        self.tearDown()
        users = User.query.all()
        prestations = Prestation.query.all()
        reviews = Review.query.all()
        self.assertEqual(len(users), 0)
        self.assertEqual(len(prestations), 0)
        self.assertEqual(len(reviews), 0)
        self.setUp()

    def setUp(self):
        super().setUp()

        # Configuration de l'API
        self.api = self.create_test_api("PublicReviews")
        self.api.add_namespace(auth_api, path="/auth")
        self.api.add_namespace(reviews_api, path="/reviews")

        self.client = self.app.test_client()

        # Créer utilisateurs
        self.user = User(
            first_name="Jean-Pierre",
            last_name="Dupont",
            email="jp@test.com",
            password="Testpassword123!"
        )
        self.ghost_user = User(
            first_name="Ghost",
            last_name="User",
            email="ghost@test.com",
            password="Testpassword123!"
        )
        self.save_to_db(self.user, self.ghost_user)

        # Créer prestations
        self.prestation = Prestation(name="Massage relaxant")
        self.ghost_prestation = Prestation(name="Ghot prestation")
        self.save_to_db(self.prestation, self.ghost_prestation)

        # Créer avis
        self.review_1 = Review(text="Super séance !", rating=5, user=self.user, prestation=self.prestation)
        self.review_2 = Review(text="Avis fantôme", rating=4, user=self.ghost_user, prestation=self.ghost_prestation)
        self.save_to_db(self.review_1, self.review_2)

        # Instancier les couches métier
        self.service = ReviewService()
        self.facade = Facade()

    def test_service_formats_author_names(self):
        results = self.service.get_all_public_reviews()
        formatted_names = []

        for r in results:
            user = r.get('user', {})
            first = user.get('first_name', '')
            last = user.get('last_name', '')
            formatted_names.append(f"{first} {last}")

        self.assertIn("Jean-Pierre D.", formatted_names)
        self.assertIn("Utilisateur anonyme ", formatted_names)

    def test_service_output_structure(self):
        results = self.service.get_all_public_reviews()
        for r in results:
            self.assertIn("id", r)
            self.assertIn("rating", r)
            self.assertIn("text", r)
            self.assertIn("user", r)
            self.assertIn("first_name", r["user"])
            self.assertIn("last_name", r["user"])
            self.assertNotIn("prestation", r)
            self.assertNotIn("created_at", r)

    def test_facade_returns_clean_data(self):
        results = self.facade.get_all_public_reviews()
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertIn("user", r)
            self.assertIn("first_name", r["user"])
            self.assertIn("last_name", r["user"])

    def test_public_api_accessible_without_auth(self):
        response = self.client.get("/reviews/public-reviews")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_public_api_does_not_expose_sensitive_fields(self):
        response = self.client.get("/reviews/public-reviews")
        data = response.get_json()
        for r in data:
            self.assertNotIn("user_id", r)
            self.assertNotIn("prestation_id", r)
            self.assertNotIn("prestation", r)
            self.assertNotIn("created_at", r)


if __name__ == "__main__":
    unittest.main()
