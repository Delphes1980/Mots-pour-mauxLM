#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from app.models.user import User
from app.models.prestation import Prestation


class TestReviewRepositoryComprehensive(unittest.TestCase):
    """Tests unitaires complets pour ReviewRepository"""

    @patch('app.db')
    @patch('app.persistence.ReviewRepository.Review')
    @patch('app.persistence.ReviewRepository.rating_validation')
    @patch('app.persistence.ReviewRepository.text_field_validation')
    @patch('app.persistence.ReviewRepository.type_validation')
    @patch('app.persistence.ReviewRepository.is_valid_uuid4')
    def test_create_review(self, mock_uuid_val, mock_type_val, mock_text_val, mock_rating_val, mock_review_class, mock_db):
        """Test création review"""
        from app.persistence.ReviewRepository import ReviewRepository
        
        mock_rating_val.return_value = None
        mock_text_val.return_value = None
        mock_type_val.return_value = None
        mock_uuid_val.return_value = True

        mock_review_instance = Mock()
        mock_review_class.return_value = mock_review_instance

        mock_session = Mock()
        mock_db.session = mock_session
        
        mock_user = Mock()
        mock_user.id = 'user-id'
        mock_prestation = Mock()
        mock_prestation.id = 'prestation-id'
        
        repo = ReviewRepository()
        repo.get_by_user_and_prestation = Mock(return_value=None)
        
        result = repo.create_review('Excellent', 5, mock_user, mock_prestation)
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        self.assertIsNotNone(result)

    @patch('app.db')
    def test_get_by_user_and_prestation(self, mock_db):
        """Test récupération review par user et prestation"""
        from app.persistence.ReviewRepository import ReviewRepository
        
        mock_review = Mock()
        mock_session = Mock()
        mock_query = Mock()
        mock_filter_by = Mock()
        mock_filter_by.first.return_value = mock_review
        mock_query.filter_by.return_value = mock_filter_by
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = ReviewRepository()
        result = repo.get_by_user_and_prestation('user_id', 'prestation_id')
        
        self.assertEqual(result, mock_review)

    @patch('app.db')
    def test_get_by_prestation_id(self, mock_db):
        """Test récupération reviews par prestation"""
        from app.persistence.ReviewRepository import ReviewRepository
        
        mock_reviews = [Mock(), Mock()]
        mock_session = Mock()
        mock_query = Mock()
        mock_filter_by = Mock()
        mock_filter_by.all.return_value = mock_reviews
        mock_query.filter_by.return_value = mock_filter_by
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = ReviewRepository()
        result = repo.get_by_prestation_id('prestation_id')
        
        self.assertEqual(result, mock_reviews)

    @patch('app.db')
    def test_get_by_user_id(self, mock_db):
        """Test récupération reviews par utilisateur"""
        from app.persistence.ReviewRepository import ReviewRepository
        
        mock_reviews = [Mock(), Mock()]
        mock_session = Mock()
        mock_query = Mock()
        mock_filter_by = Mock()
        mock_filter_by.all.return_value = mock_reviews
        mock_query.filter_by.return_value = mock_filter_by
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = ReviewRepository()
        result = repo.get_by_user_id('user_id')
        
        self.assertEqual(result, mock_reviews)

    @patch('app.db')
    def test_get_all_public_reviews(self, mock_db):
        """Test récupération toutes reviews publiques"""
        from app.persistence.ReviewRepository import ReviewRepository
        
        mock_reviews = [Mock(), Mock()]
        mock_session = Mock()
        mock_query = Mock()
        mock_options = Mock()
        mock_options.all.return_value = mock_reviews
        mock_query.options.return_value = mock_options
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = ReviewRepository()
        result = repo.get_all_public_reviews()
        
        self.assertEqual(result, mock_reviews)

    @patch('app.db')
    @patch('app.utils.is_valid_uuid4')
    def test_reassign_reviews_from_user(self, mock_uuid_val, mock_db):
        """Test réassignation reviews utilisateur"""
        from app.persistence.ReviewRepository import ReviewRepository
        from uuid import uuid4
        
        mock_uuid_val.return_value = True
        mock_old_user = Mock()
        mock_new_user = Mock()
        mock_reviews = [Mock(), Mock()]
        mock_session = Mock()
        mock_session.query.return_value.get.side_effect = [mock_old_user, mock_new_user]
        mock_db.session = mock_session
        
        repo = ReviewRepository()
        repo.get_by_user_id = Mock(return_value=mock_reviews)
        
        result = repo.reassign_reviews_from_user(str(uuid4()), str(uuid4()))
        
        self.assertEqual(result, 2)
        mock_session.commit.assert_called_once()

    @patch('app.db')
    @patch('app.utils.is_valid_uuid4')
    def test_reassign_reviews_from_prestation(self, mock_uuid_val, mock_db):
        """Test réassignation reviews prestation"""
        from app.persistence.ReviewRepository import ReviewRepository
        from uuid import uuid4
        
        mock_uuid_val.return_value = True
        mock_old_prestation = Mock()
        mock_new_prestation = Mock()
        mock_reviews = [Mock(), Mock()]
        mock_session = Mock()
        mock_session.query.return_value.get.side_effect = [mock_old_prestation, mock_new_prestation]
        mock_db.session = mock_session
        
        repo = ReviewRepository()
        repo.get_by_prestation_id = Mock(return_value=mock_reviews)
        
        result = repo.reassign_reviews_from_prestation(str(uuid4()), str(uuid4()))
        
        self.assertEqual(result, 2)
        mock_session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()