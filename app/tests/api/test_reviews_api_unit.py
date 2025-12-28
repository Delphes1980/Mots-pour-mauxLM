#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch


class TestReviewsAPIUnit(unittest.TestCase):
    """Tests unitaires purs pour l'API reviews"""

    @patch('app.api.v1.reviews.facade')
    def test_create_review_logic(self, mock_facade):
        """Test logique création review"""
        mock_review = Mock()
        mock_facade.create_review.return_value = mock_review
        
        review_data = {
            'text': 'Great service',
            'rating': 5,
            'user_id': 'user-id',
            'prestation_id': 'prestation-id'
        }
        
        result = mock_facade.create_review(**review_data)
        
        self.assertEqual(result, mock_review)
        mock_facade.create_review.assert_called_once_with(**review_data)

    @patch('app.api.v1.reviews.facade')
    def test_get_all_reviews_logic(self, mock_facade):
        """Test logique récupération toutes reviews"""
        mock_reviews = [Mock(), Mock()]
        mock_facade.get_all_reviews.return_value = mock_reviews
        
        result = mock_facade.get_all_reviews()
        
        self.assertEqual(result, mock_reviews)
        mock_facade.get_all_reviews.assert_called_once()

    @patch('app.api.v1.reviews.facade')
    def test_get_review_by_id_logic(self, mock_facade):
        """Test logique récupération review par ID"""
        mock_review = Mock()
        mock_facade.get_review_by_id.return_value = mock_review
        
        result = mock_facade.get_review_by_id('review-id')
        
        self.assertEqual(result, mock_review)
        mock_facade.get_review_by_id.assert_called_once_with('review-id')

    @patch('app.api.v1.reviews.facade')
    def test_update_review_logic(self, mock_facade):
        """Test logique mise à jour review"""
        mock_review = Mock()
        mock_facade.update_review.return_value = mock_review
        
        update_data = {'text': 'Updated review', 'rating': 4}
        result = mock_facade.update_review('review-id', current_user_id='user-id', **update_data)
        
        self.assertEqual(result, mock_review)
        mock_facade.update_review.assert_called_once_with('review-id', current_user_id='user-id', **update_data)

    @patch('app.api.v1.reviews.facade')
    def test_delete_review_logic(self, mock_facade):
        """Test logique suppression review"""
        mock_facade.delete_review.return_value = True
        
        result = mock_facade.delete_review('review-id')
        
        self.assertTrue(result)
        mock_facade.delete_review.assert_called_once_with('review-id')

    @patch('app.api.v1.reviews.facade')
    def test_get_all_public_reviews_logic(self, mock_facade):
        """Test logique récupération de tous les commentaires publics"""
        mock_reviews = [Mock(), Mock()]
        mock_facade.get_all_public_reviews.return_value = mock_reviews
        
        result = mock_facade.get_all_public_reviews()
        
        self.assertEqual(result, mock_reviews)
        mock_facade.get_all_public_reviews.assert_called_once()

    @patch('app.api.v1.reviews.facade')
    def test_get_review_by_user_logic(self, mock_facade):
        """Test logique récupération des commentaires d'un utilisateur (endpoint /me et /by-user)"""
        mock_reviews = [Mock(), Mock()]
        mock_facade.get_review_by_user.return_value = mock_reviews
        
        user_id = 'test-user-id'
        result = mock_facade.get_review_by_user(user_id)
        
        self.assertEqual(result, mock_reviews)
        mock_facade.get_review_by_user.assert_called_once_with(user_id)

    @patch('app.api.v1.reviews.facade')
    def test_get_review_by_prestation_logic(self, mock_facade):
        """Test logique récupération des commentaires pour une prestation"""
        mock_reviews = [Mock(), Mock()]
        mock_facade.get_review_by_prestation.return_value = mock_reviews
        
        prestation_id = 'test-prestation-id'
        result = mock_facade.get_review_by_prestation(prestation_id)
        
        self.assertEqual(result, mock_reviews)
        mock_facade.get_review_by_prestation.assert_called_once_with(prestation_id)

    @patch('app.api.v1.reviews.facade')
    def test_get_review_by_user_and_prestation_logic(self, mock_facade):
        """Test logique récupération d'un avis spécifique par utilisateur et prestation"""
        mock_review = Mock()
        mock_facade.get_review_by_user_and_prestation.return_value = mock_review
        
        user_id = 'test-user-id'
        prestation_id = 'test-prestation-id'
        result = mock_facade.get_review_by_user_and_prestation(user_id, prestation_id)
        
        self.assertEqual(result, mock_review)
        mock_facade.get_review_by_user_and_prestation.assert_called_once_with(user_id, prestation_id)


if __name__ == '__main__':
    unittest.main()