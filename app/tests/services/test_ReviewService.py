import unittest
from app.tests.base_test import BaseTest
from app.services.ReviewService import ReviewService
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review


class TestReviewService(BaseTest):
    """Tests d'intégration pour ReviewService"""

    def setUp(self):
        super().setUp()
        self.service = ReviewService()
        # S'assurer que les repositories utilisent la même instance de db
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
        
        self.valid_review_data = {
            'rating': 5,
            'text': 'Excellent service',
            'user_id': self.user.id,
            'prestation_id': self.prestation.id
        }

    # ==================== Tests create_review ====================

    def test_create_review_success(self):
        """Test de création réussie d'un avis"""
        result = self.service.create_review(**self.valid_review_data)
        
        self.assertIsInstance(result, Review)
        self.assertEqual(result.rating, 5)
        self.assertEqual(result.text, 'Excellent service')
        self.assertEqual(result._user_id, self.user.id)
        self.assertEqual(result._prestation_id, self.prestation.id)

    def test_create_review_invalid_rating_too_low(self):
        """Test avec une note trop basse"""
        self.valid_review_data['rating'] = 0
        
        with self.assertRaises(ValueError):
            self.service.create_review(**self.valid_review_data)

    def test_create_review_invalid_rating_too_high(self):
        """Test avec une note trop haute"""
        self.valid_review_data['rating'] = 6
        
        with self.assertRaises(ValueError):
            self.service.create_review(**self.valid_review_data)

    def test_create_review_text_too_short(self):
        """Test avec un texte trop court"""
        self.valid_review_data['text'] = 'A'
        
        with self.assertRaises(ValueError):
            self.service.create_review(**self.valid_review_data)

    def test_create_review_text_too_long(self):
        """Test avec un texte trop long"""
        self.valid_review_data['text'] = 'A' * 501
        
        with self.assertRaises(ValueError):
            self.service.create_review(**self.valid_review_data)

    def test_create_review_missing_user_id(self):
        """Test sans user_id"""
        self.valid_review_data['user_id'] = None
        
        with self.assertRaises(ValueError) as context:
            self.service.create_review(**self.valid_review_data)
        self.assertIn("user_id", str(context.exception).lower())

    def test_create_review_invalid_user_id_format(self):
        """Test avec un format d'user_id invalide"""
        self.valid_review_data['user_id'] = 'invalid-uuid'
        
        with self.assertRaises(ValueError) as context:
            self.service.create_review(**self.valid_review_data)
        self.assertIn("format", str(context.exception).lower())

    def test_create_review_missing_prestation_id(self):
        """Test sans prestation_id"""
        self.valid_review_data['prestation_id'] = None
        
        with self.assertRaises(ValueError) as context:
            self.service.create_review(**self.valid_review_data)
        self.assertIn("prestation", str(context.exception).lower())

    def test_create_review_invalid_prestation_id_format(self):
        """Test avec un format de prestation_id invalide"""
        self.valid_review_data['prestation_id'] = 'invalid-uuid'
        
        with self.assertRaises(ValueError) as context:
            self.service.create_review(**self.valid_review_data)
        self.assertIn("format", str(context.exception).lower())

    def test_create_review_user_not_found(self):
        """Test quand l'utilisateur n'existe pas"""
        self.valid_review_data['user_id'] = '12345678-1234-1234-1234-123456789012'
        
        with self.assertRaises(ValueError) as context:
            self.service.create_review(**self.valid_review_data)
        self.assertIn("introuvable", str(context.exception).lower())

    def test_create_review_prestation_not_found(self):
        """Test quand la prestation n'existe pas"""
        self.valid_review_data['prestation_id'] = '87654321-4321-4321-4321-210987654321'
        
        with self.assertRaises(ValueError) as context:
            self.service.create_review(**self.valid_review_data)
        self.assertIn("prestation", str(context.exception).lower())

    def test_create_review_already_exists(self):
        """Test quand un avis existe déjà"""
        # Créer un premier avis
        self.service.create_review(**self.valid_review_data)
        
        # Tenter de créer un second avis pour la même combinaison
        with self.assertRaises(ValueError) as context:
            self.service.create_review(**self.valid_review_data)
        self.assertIn("existe", str(context.exception).lower())

    # ==================== Tests get_review_by_id ====================

    def test_get_review_by_id_success(self):
        """Test de récupération réussie d'un avis par ID"""
        created_review = self.service.create_review(**self.valid_review_data)
        
        result = self.service.get_review_by_id(created_review.id)
        
        self.assertEqual(result.id, created_review.id)
        self.assertEqual(result.rating, 5)
        self.assertEqual(result.text, 'Excellent service')

    def test_get_review_by_id_missing_id(self):
        """Test sans ID"""
        with self.assertRaises(ValueError) as context:
            self.service.get_review_by_id(None)
        self.assertIn("review_id", str(context.exception).lower())

    def test_get_review_by_id_invalid_format(self):
        """Test avec un format d'ID invalide"""
        with self.assertRaises(ValueError) as context:
            self.service.get_review_by_id('invalid-uuid')
        self.assertIn("format", str(context.exception).lower())

    def test_get_review_by_id_not_found(self):
        """Test quand l'avis n'existe pas"""
        with self.assertRaises(ValueError) as context:
            self.service.get_review_by_id('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        self.assertIn("non trouvé", str(context.exception).lower())

    # ==================== Tests get_all_reviews ====================

    def test_get_all_reviews_with_data(self):
        """Test de récupération de tous les avis"""
        # Créer plusieurs avis
        review1 = self.service.create_review(**self.valid_review_data)
        
        # Créer un second utilisateur et prestation pour un autre avis
        user2 = User(
            first_name="Marie",
            last_name="Martin",
            email="marie.martin@test.com",
            password="MotDePasse123!",
            is_admin=False
        )
        self.db.session.add(user2)
        
        prestation2 = Prestation(name="Consultation")
        self.db.session.add(prestation2)
        self.db.session.commit()
        
        review2_data = {
            'rating': 4,
            'text': 'Très bien',
            'user_id': user2.id,
            'prestation_id': prestation2.id
        }
        review2 = self.service.create_review(**review2_data)
        
        result = self.service.get_all_reviews()
        
        self.assertEqual(len(result), 2)
        review_ids = [r.id for r in result]
        self.assertIn(review1.id, review_ids)
        self.assertIn(review2.id, review_ids)

    def test_get_all_reviews_empty(self):
        """Test quand il n'y a aucun avis"""
        result = self.service.get_all_reviews()
        self.assertEqual(result, [])

    # ==================== Tests get_review_by_prestation ====================

    def test_get_review_by_prestation_success(self):
        """Test de récupération des avis par prestation"""
        created_review = self.service.create_review(**self.valid_review_data)
        
        result = self.service.get_review_by_prestation(self.prestation.id)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, created_review.id)

    def test_get_review_by_prestation_missing_id(self):
        """Test sans prestation_id"""
        with self.assertRaises(ValueError) as context:
            self.service.get_review_by_prestation(None)
        self.assertIn("prestation_id", str(context.exception).lower())

    def test_get_review_by_prestation_invalid_format(self):
        """Test avec un format de prestation_id invalide"""
        with self.assertRaises(ValueError) as context:
            self.service.get_review_by_prestation('invalid-uuid')
        self.assertIn("format", str(context.exception).lower())

    def test_get_review_by_prestation_empty(self):
        """Test avec une prestation sans avis"""
        result = self.service.get_review_by_prestation(self.prestation.id)
        self.assertEqual(result, [])

    # ==================== Tests get_review_by_user ====================

    def test_get_review_by_user_success(self):
        """Test de récupération des avis par utilisateur"""
        created_review = self.service.create_review(**self.valid_review_data)
        
        result = self.service.get_review_by_user(self.user.id)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, created_review.id)

    def test_get_review_by_user_missing_id(self):
        """Test sans user_id"""
        with self.assertRaises(ValueError) as context:
            self.service.get_review_by_user(None)
        self.assertIn("user_id", str(context.exception).lower())

    def test_get_review_by_user_invalid_format(self):
        """Test avec un format d'user_id invalide"""
        with self.assertRaises(ValueError) as context:
            self.service.get_review_by_user('invalid-uuid')
        self.assertIn("format", str(context.exception).lower())

    def test_get_review_by_user_not_found(self):
        """Test quand l'utilisateur n'existe pas"""
        with self.assertRaises(ValueError) as context:
            self.service.get_review_by_user('12345678-1234-1234-1234-123456789012')
        self.assertIn("non trouvé", str(context.exception).lower())

    def test_get_review_by_user_empty(self):
        """Test avec un utilisateur sans avis"""
        result = self.service.get_review_by_user(self.user.id)
        self.assertEqual(result, [])

    # ==================== Tests update_review ====================

    def test_update_review_success_rating(self):
        """Test de mise à jour réussie de la note"""
        created_review = self.service.create_review(**self.valid_review_data)
        
        result = self.service.update_review(created_review.id, rating=4)
        
        self.assertEqual(result.rating, 4)
        self.assertEqual(result.text, 'Excellent service')  # Inchangé

    def test_update_review_success_text(self):
        """Test de mise à jour réussie du texte"""
        created_review = self.service.create_review(**self.valid_review_data)
        
        result = self.service.update_review(created_review.id, text='Nouveau commentaire')
        
        self.assertEqual(result.text, 'Nouveau commentaire')
        self.assertEqual(result.rating, 5)  # Inchangé

    def test_update_review_success_both(self):
        """Test de mise à jour réussie des deux champs"""
        created_review = self.service.create_review(**self.valid_review_data)
        
        result = self.service.update_review(created_review.id, rating=3, text='Commentaire modifié')
        
        self.assertEqual(result.rating, 3)
        self.assertEqual(result.text, 'Commentaire modifié')

    def test_update_review_missing_id(self):
        """Test sans review_id"""
        with self.assertRaises(ValueError) as context:
            self.service.update_review(None, rating=4)
        self.assertIn("review_id", str(context.exception).lower())

    def test_update_review_invalid_id_format(self):
        """Test avec un format d'ID invalide"""
        with self.assertRaises(ValueError) as context:
            self.service.update_review('invalid-uuid', rating=4)
        self.assertIn("format", str(context.exception).lower())

    def test_update_review_not_found(self):
        """Test quand l'avis n'existe pas"""
        with self.assertRaises(ValueError) as context:
            self.service.update_review('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', rating=4)
        self.assertIn("non trouvé", str(context.exception).lower())

    def test_update_review_invalid_rating(self):
        """Test avec une note invalide"""
        created_review = self.service.create_review(**self.valid_review_data)
        
        with self.assertRaises(ValueError):
            self.service.update_review(created_review.id, rating=0)

    def test_update_review_invalid_text(self):
        """Test avec un texte invalide"""
        created_review = self.service.create_review(**self.valid_review_data)
        
        with self.assertRaises(ValueError):
            self.service.update_review(created_review.id, text='A')

    # ==================== Tests delete_review ====================

    def test_delete_review_success(self):
        """Test de suppression réussie d'un avis"""
        created_review = self.service.create_review(**self.valid_review_data)
        
        result = self.service.delete_review(created_review.id)
        
        self.assertTrue(result)
        
        # Vérifier que l'avis n'existe plus
        with self.assertRaises(ValueError):
            self.service.get_review_by_id(created_review.id)

    def test_delete_review_missing_id(self):
        """Test sans review_id"""
        with self.assertRaises(ValueError) as context:
            self.service.delete_review(None)
        self.assertIn("review_id", str(context.exception).lower())

    def test_delete_review_invalid_id_format(self):
        """Test avec un format d'ID invalide"""
        with self.assertRaises(ValueError) as context:
            self.service.delete_review('invalid-uuid')
        self.assertIn("format", str(context.exception).lower())

    def test_delete_review_not_found(self):
        """Test quand l'avis n'existe pas"""
        with self.assertRaises(ValueError) as context:
            self.service.delete_review('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        self.assertIn("non trouvé", str(context.exception).lower())


if __name__ == '__main__':
    unittest.main()