#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from sqlalchemy.exc import SQLAlchemyError


class TestBaseRepositoryUnit(unittest.TestCase):
    """Tests unitaires purs pour BaseRepository"""

    @patch('app.db')
    def test_create_success(self, mock_db):
        """Test création d'entité réussie"""
        from app.persistence.BaseRepository import BaseRepository
        
        mock_model_class = Mock()
        mock_entity = Mock()
        mock_model_class.return_value = mock_entity
        mock_session = Mock()
        mock_db.session = mock_session
        
        repo = BaseRepository(mock_model_class)
        result = repo.create(name='test')
        
        mock_model_class.assert_called_once_with(name='test')
        mock_session.add.assert_called_once_with(mock_entity)
        mock_session.commit.assert_called_once()
        self.assertEqual(result, mock_entity)

    @patch('app.db')
    def test_create_failure_rollback(self, mock_db):
        """Test rollback en cas d'erreur"""
        from app.persistence.BaseRepository import BaseRepository
        
        mock_model_class = Mock()
        mock_session = Mock()
        mock_session.commit.side_effect = SQLAlchemyError("Test error")
        mock_db.session = mock_session
        
        repo = BaseRepository(mock_model_class)
        
        with self.assertRaises(SQLAlchemyError):
            repo.create(name='test')
        
        mock_session.rollback.assert_called_once()

    @patch('app.db')
    def test_get_by_id(self, mock_db):
        """Test récupération par ID"""
        from app.persistence.BaseRepository import BaseRepository
        
        mock_model_class = Mock()
        mock_entity = Mock()
        mock_session = Mock()
        mock_session.query.return_value.get.return_value = mock_entity
        mock_db.session = mock_session
        
        repo = BaseRepository(mock_model_class)
        result = repo.get_by_id('test-id')
        
        mock_session.query.assert_called_once_with(mock_model_class)
        self.assertEqual(result, mock_entity)

    @patch('app.db')
    def test_delete_success(self, mock_db):
        """Test suppression réussie"""
        from app.persistence.BaseRepository import BaseRepository
        
        mock_model_class = Mock()
        mock_entity = Mock()
        mock_session = Mock()
        mock_session.query.return_value.get.return_value = mock_entity
        mock_db.session = mock_session
        
        repo = BaseRepository(mock_model_class)
        result = repo.delete('test-id')
        
        mock_session.delete.assert_called_once_with(mock_entity)
        mock_session.commit.assert_called_once()
        self.assertTrue(result)

    @patch('app.db')
    def test_get_by_attribute(self, mock_db):
        """Test récupération par attribut spécifique"""
        from app.persistence.BaseRepository import BaseRepository
        
        mock_model_class = Mock()
        mock_entity = Mock()
        mock_session = Mock()
        mock_query = Mock()
        mock_filter_by = Mock()
        
        # Simulation de la chaîne : query().filter_by().first()
        mock_filter_by.first.return_value = mock_entity
        mock_query.filter_by.return_value = mock_filter_by
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = BaseRepository(mock_model_class)
        result = repo.get_by_attribute('email', 'test@test.com')
        
        mock_query.filter_by.assert_called_once()
        self.assertEqual(result, mock_entity)

    @patch('app.db')
    def test_get_all(self, mock_db):
        """Test récupération de toutes les entités"""
        from app.persistence.BaseRepository import BaseRepository
        
        mock_model_class = Mock()
        mock_entities = [Mock(), Mock()]
        mock_session = Mock()
        mock_query = Mock()
        
        mock_query.all.return_value = mock_entities
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = BaseRepository(mock_model_class)
        result = repo.get_all()
        
        mock_query.all.assert_called_once()
        self.assertEqual(result, mock_entities)

    @patch('app.db')
    def test_update_success(self, mock_db):
        """Test mise à jour réussie"""
        from app.persistence.BaseRepository import BaseRepository
        
        mock_model_class = Mock()
        mock_entity = Mock()
        mock_session = Mock()
        mock_db.session = mock_session
        
        repo = BaseRepository(mock_model_class)
        # On mock get_by_id pour qu'il trouve l'entité
        repo.get_by_id = Mock(return_value=mock_entity)
        
        result = repo.update('test-id', name='nouveau nom')
        
        self.assertEqual(result, mock_entity)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_entity)

    @patch('app.db')
    def test_update_not_found(self, mock_db):
        """Test mise à jour sur entité inexistante"""
        from app.persistence.BaseRepository import BaseRepository
        
        mock_model_class = Mock()
        repo = BaseRepository(mock_model_class)
        repo.get_by_id = Mock(return_value=None)
        
        result = repo.update('unknown-id', name='test')
        
        self.assertIsNone(result)

    @patch('app.db')
    def test_delete_not_found(self, mock_db):
        """Test suppression sur entité inexistante"""
        from app.persistence.BaseRepository import BaseRepository
        
        mock_model_class = Mock()
        repo = BaseRepository(mock_model_class)
        repo.get_by_id = Mock(return_value=None)
        
        result = repo.delete('unknown-id')
        
        self.assertFalse(result)

    @patch('app.db')
    def test_delete_failure_rollback(self, mock_db):
        """Test rollback en cas d'erreur de suppression"""
        from app.persistence.BaseRepository import BaseRepository
        
        mock_model_class = Mock()
        mock_entity = Mock()
        mock_session = Mock()
        # On simule une erreur lors du commit
        mock_session.commit.side_effect = SQLAlchemyError("DB Error")
        mock_db.session = mock_session
        
        repo = BaseRepository(mock_model_class)
        repo.get_by_id = Mock(return_value=mock_entity)
        
        with self.assertRaises(SQLAlchemyError):
            repo.delete('test-id')
        
        mock_session.rollback.assert_called_once()


if __name__ == '__main__':
    unittest.main()