#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
from app.utils import CustomError


class TestReviewServiceUnit(unittest.TestCase):
    """Tests unitaires complets pour ReviewService"""

    @patch('app.services.ReviewService.ReviewRepository')
    @patch('app.services.ReviewService.UserRepository')
    @patch('app.services.ReviewService.PrestationRepository')
    @patch('app.utils.rating_validation')
    @patch('app.utils.text_field_validation')
    @patch('app.utils.validate_entity_id')
    def test_create_review_success(self, mock_val_id, mock_text_val, mock_rating_val, mock_prest_repo, mock_user_repo, mock_review_repo):
        """Test création review réussie"""
        from app.services.ReviewService import ReviewService
        
        mock_val_id.return_value = 'valid_id'
        mock_user_repo.return_value.get_by_id.return_value = Mock()
        mock_prest_repo.return_value.get_by_id.return_value = Mock()
        mock_review_repo.return_value.get_by_user_and_prestation.return_value = None

        mock_review = Mock()
        mock_review_repo.return_value.create_review.return_value = mock_review
        
        service = ReviewService()
        result = service.create_review(
            text='Excellent service',
            rating=5,
            user_id=str(uuid4()),
            prestation_id=str(uuid4())
        )
        
        self.assertEqual(result, mock_review)

    @patch('app.services.ReviewService.ReviewRepository')
    def test_get_review_by_id(self, mock_repo_class):
        """Test récupération review par ID"""
        from app.services.ReviewService import ReviewService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_review = Mock()
        mock_repo.get_by_id.return_value = mock_review
        
        service = ReviewService()
        result = service.get_review_by_id(str(uuid4()))
        
        self.assertEqual(result, mock_review)

    @patch('app.services.ReviewService.ReviewRepository')
    def test_get_all_reviews(self, mock_repo_class):
        """Test récupération toutes reviews"""
        from app.services.ReviewService import ReviewService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_user = Mock()
        mock_user.id = str(uuid4())
        mock_user.first_name = "Jean-Pierre"
        mock_user.last_name = "Dupont"

        mock_review = Mock()
        mock_review.id = str(uuid4())
        mock_review.user = mock_user
        mock_review.rating = 5
        mock_review.text = "Test"

        mock_repo.get_all_public_reviews.return_value = [mock_review]
        
        service = ReviewService()
        result = service.get_all_public_reviews()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['user']['first_name'], "Jean-Pierre")

    @patch('app.services.ReviewService.ReviewRepository')
    @patch('app.utils.validate_entity_id')
    def test_get_reviews_by_user(self, mock_val_id, mock_repo_class):
        """Test récupération reviews par utilisateur"""
        from app.services.ReviewService import ReviewService
        
        mock_val_id.return_value = 'valid_id'
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_reviews = [Mock(), Mock()]
        mock_repo.get_by_user_id.return_value = mock_reviews
        
        with patch('app.services.ReviewService.UserRepository') as mock_user_repo:
            mock_user_repo.return_value.get_by_id.return_value = Mock()
            service = ReviewService()
            result = service.get_review_by_user(str(uuid4()))
            self.assertEqual(result, mock_reviews)

    @patch('app.services.ReviewService.ReviewRepository')
    @patch('app.services.ReviewService.PrestationRepository')
    @patch('app.utils.validate_entity_id')
    def test_get_reviews_by_prestation(self, mock_val_id, mock_prest_repo_class, mock_repo_class):
        """Test récupération reviews par prestation"""
        from app.services.ReviewService import ReviewService
        
        mock_val_id.return_value = 'valid_id'

        mock_prest_repo = Mock()
        mock_prest_repo_class.return_value = mock_prest_repo
        mock_prest_repo.get_by_id.return_value = Mock()

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_reviews = [Mock(), Mock()]
        mock_repo.get_by_prestation_id.return_value = mock_reviews
        
        service = ReviewService()
        result = service.get_review_by_prestation(str(uuid4()))
        
        self.assertEqual(result, mock_reviews)
        mock_prest_repo.get_by_id.assert_called_once()

    @patch('app.services.ReviewService.ReviewRepository')
    @patch('app.services.ReviewService.UserRepository')
    @patch('app.services.ReviewService.PrestationRepository')
    @patch('app.utils.validate_entity_id')
    def test_update_review(self, mock_val_id, mock_prest_repo, mock_user_repo, mock_repo_class):
        """Test mise à jour review"""
        from app.services.ReviewService import ReviewService
        
        mock_val_id.return_value = str(uuid4())

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        valid_user_id = str(uuid4())
        mock_review = Mock()
        mock_review.user_id = valid_user_id
        mock_review.prestation_id = str(uuid4())
        mock_repo.get_by_id.return_value = mock_review

        mock_current_user = Mock()
        mock_current_user.is_admin = False
        mock_user_repo.return_value.get_by_id.return_value = mock_current_user
        mock_prest_repo.return_value.get_by_id.return_value = Mock()
        
        service = ReviewService()
        result = service.update_review(
            review_id=str(uuid4()),
            current_user_id=valid_user_id,
            text='Nouveau texte',
            rating=4
        )
        
        self.assertEqual(result, mock_repo.update.return_value)

    @patch('app.services.ReviewService.ReviewRepository')
    def test_delete_review(self, mock_repo_class):
        """Test suppression review"""
        from app.services.ReviewService import ReviewService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.delete.return_value = True
        
        service = ReviewService()
        result = service.delete_review(str(uuid4()))
        
        self.assertTrue(result)

    @patch('app.services.ReviewService.ReviewRepository')
    @patch('app.services.ReviewService.UserRepository')
    @patch('app.services.ReviewService.PrestationRepository')
    @patch('app.utils.validate_entity_id')
    def test_get_review_by_user_and_prestation(self, mock_val_id, mock_prest_repo, mock_user_repo, mock_repo_class):
        """Test récupération review par user et prestation"""
        from app.services.ReviewService import ReviewService
        
        mock_val_id.return_value = 'valid_id'
        mock_user_repo.return_value.get_by_id.return_value = Mock()
        mock_prest_repo.return_value.get_by_id.return_value = Mock()

        mock_repo = Mock()
        mock_review = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_user_and_prestation.return_value = mock_review
        
        service = ReviewService()
        result = service.get_review_by_user_and_prestation(str(uuid4()), str(uuid4()))
        
        self.assertEqual(result, mock_review)

    @patch('app.services.ReviewService.ReviewRepository')
    def test_get_all_public_reviews_formatted(self, mock_repo_class):
        """Test la logique de formatage des noms pour les avis publics"""
        from app.services.ReviewService import ReviewService
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        # Simulation d'un utilisateur avec un prénom composé
        mock_user = Mock()
        mock_user.id = str(uuid4())
        mock_user.first_name = "jean-pierre"
        mock_user.last_name = "dupont"
        
        mock_review = Mock()
        mock_review.id = str(uuid4())
        mock_review.rating = 5
        mock_review.text = "Super"
        mock_review.user = mock_user
        
        mock_repo.get_all_public_reviews.return_value = [mock_review]
        
        service = ReviewService()
        result = service.get_all_public_reviews()
        
        # Vérification du formatage (Jean-Pierre D.)
        self.assertEqual(result[0]['user']['first_name'], "Jean-Pierre")
        self.assertEqual(result[0]['user']['last_name'], "D.")

    @patch('app.services.ReviewService.ReviewRepository')
    @patch('app.utils.validate_entity_id')
    def test_get_review_by_id_not_found(self, mock_validate_id, mock_repo_class):
        """Test erreur 404 si le commentaire n'existe pas"""
        from app.services.ReviewService import ReviewService
        
        mock_validate_id.return_value = 'valid-id'
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_by_id.return_value = None
        
        service = ReviewService()
        with self.assertRaises(CustomError) as cm:
            service.get_review_by_id(str(uuid4()))
        self.assertEqual(cm.exception.status_code, 404)

    @patch('app.services.ReviewService.ReviewRepository')
    @patch('app.services.ReviewService.UserRepository')
    @patch('app.utils.validate_entity_id')
    def test_reassign_reviews_from_user_success(self, mock_validate_id, mock_user_repo, mock_review_repo):
        """Test réassignation des avis d'un utilisateur à un autre (ex: suppression compte)"""
        from app.services.ReviewService import ReviewService
        
        mock_validate_id.return_value = 'valid-id'

        mock_old_user = Mock()
        mock_new_user = Mock()
        mock_user_repo.return_value.get_by_id.side_effect = [mock_old_user, mock_new_user] # Old et New user
        
        mock_review = Mock()
        mock_review_repo.return_value.get_by_user_id.return_value = [mock_review]
        
        service = ReviewService()
        result = service.reassign_reviews_from_user(str(uuid4()), str(uuid4()))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].user, mock_new_user)

    @patch('app.services.ReviewService.ReviewRepository')
    @patch('app.services.ReviewService.PrestationRepository')
    @patch('app.utils.validate_entity_id')
    def test_reassign_reviews_from_prestation_success(self, mock_validate_id, mock_prest_repo, mock_review_repo):
        """Test réassignation des avis d'une prestation à une autre (ex: prestation fantôme)"""
        from app.services.ReviewService import ReviewService
        
        mock_validate_id.return_value = 'valid-id'
        mock_prest_repo.return_value.get_by_id.side_effect = [Mock(), Mock()]
        
        mock_review = Mock()
        mock_review_repo.return_value.get_by_prestation_id.return_value = [mock_review]
        
        service = ReviewService()
        result = service.reassign_reviews_from_prestation(str(uuid4()), str(uuid4()))
        
        self.assertEqual(len(result), 1)
        mock_review_repo.return_value.db.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()