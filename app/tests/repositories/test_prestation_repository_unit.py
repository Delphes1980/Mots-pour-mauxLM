#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch


class TestPrestationRepositoryUnit(unittest.TestCase):
    """Tests unitaires purs pour PrestationRepository"""

    @patch('app.db')
    def test_get_all_prestations_for_user(self, mock_db):
        """Test récupération prestations pour utilisateur"""
        from app.persistence.PrestationRepository import PrestationRepository
        
        mock_prestations = [Mock(), Mock()]
        mock_session = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_prestations
        mock_session.query.return_value = mock_query
        mock_db.session = mock_session
        
        repo = PrestationRepository()
        result = repo.get_all_prestations_for_user()
        
        self.assertEqual(result, mock_prestations)

    @patch('app.db')
    @patch('app.persistence.PrestationRepository.text_field_validation')
    def test_create_prestation_success(self, mock_val, mock_db):
        """Test création de prestation réussie"""
        from app.persistence.PrestationRepository import PrestationRepository
        
        mock_val.return_value = None
        mock_session = Mock()
        mock_db.session = mock_session
        
        repo = PrestationRepository()
        # On simule que le nom n'existe pas encore
        repo.get_by_attribute = Mock(return_value=None)
        
        result = repo.create_prestation("Massage")
        
        self.assertEqual(result.name, "Massage")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('app.db')
    @patch('app.persistence.PrestationRepository.text_field_validation')
    def test_create_prestation_already_exists(self, mock_val, mock_db):
        """Test erreur si le nom de prestation existe déjà"""
        from app.persistence.PrestationRepository import PrestationRepository
        
        mock_val.return_value = None
        repo = PrestationRepository()
        # On simule qu'une prestation avec ce nom existe déjà
        repo.get_by_attribute = Mock(return_value=Mock())
        
        with self.assertRaises(ValueError) as cm:
            repo.create_prestation("Massage")
        
        self.assertIn("existe déjà", str(cm.exception))

    @patch('app.db')
    @patch('app.persistence.PrestationRepository.text_field_validation')
    def test_create_prestation_db_error(self, mock_val, mock_db):
        """Test rollback en cas d'erreur database lors de la création"""
        from app.persistence.PrestationRepository import PrestationRepository
        from sqlalchemy.exc import SQLAlchemyError
        
        mock_val.return_value = None
        mock_session = Mock()
        # On simule une erreur lors du commit
        mock_session.commit.side_effect = SQLAlchemyError("DB Error")
        mock_db.session = mock_session
        
        repo = PrestationRepository()
        repo.get_by_attribute = Mock(return_value=None)
        
        with self.assertRaises(ValueError) as cm:
            repo.create_prestation("Massage")
        
        self.assertIn("Erreur lors de la création", str(cm.exception))
        mock_session.rollback.assert_called_once()

    @patch('app.db')
    def test_create_wrapper(self, mock_db):
        """Test que la méthode create appelle bien create_prestation"""
        from app.persistence.PrestationRepository import PrestationRepository
        
        repo = PrestationRepository()
        repo.create_prestation = Mock(return_value="success")
        
        result = repo.create(name="Massage")
        
        repo.create_prestation.assert_called_once_with("Massage")
        self.assertEqual(result, "success")


if __name__ == '__main__':
    unittest.main()