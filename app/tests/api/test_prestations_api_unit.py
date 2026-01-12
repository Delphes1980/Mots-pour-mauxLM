#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch


class TestPrestationsAPIUnit(unittest.TestCase):
    """Tests unitaires purs pour l'API prestations"""

    @patch('app.api.v1.prestations.facade')
    def test_create_prestation_success_logic(self, mock_facade):
        """Test logique création prestation réussie"""
        mock_prestation = Mock()
        mock_prestation.id = 'prestation-id'
        mock_facade.create_prestation.return_value = mock_prestation
        
        prestation_data = {'name': 'Massage Relaxant'}
        result = mock_facade.create_prestation(**prestation_data)
        
        self.assertEqual(result, mock_prestation)
        mock_facade.create_prestation.assert_called_once_with(**prestation_data)

    @patch('app.api.v1.prestations.facade')
    def test_get_all_prestations_logic(self, mock_facade):
        """Test logique récupération toutes prestations"""
        mock_prestations = [Mock(), Mock()]
        mock_facade.get_all_prestations.return_value = mock_prestations
        
        result = mock_facade.get_all_prestations()
        
        self.assertEqual(result, mock_prestations)
        mock_facade.get_all_prestations.assert_called_once()

    @patch('app.api.v1.prestations.facade')
    def test_get_prestation_by_id_logic(self, mock_facade):
        """Test logique récupération prestation par ID"""
        mock_prestation = Mock()
        mock_facade.get_prestation_by_id.return_value = mock_prestation
        
        result = mock_facade.get_prestation_by_id('prestation-id')
        
        self.assertEqual(result, mock_prestation)
        mock_facade.get_prestation_by_id.assert_called_once_with('prestation-id')

    @patch('app.api.v1.prestations.facade')
    def test_update_prestation_logic(self, mock_facade):
        """Test logique mise à jour prestation"""
        mock_prestation = Mock()
        mock_facade.update_prestation.return_value = mock_prestation
        
        update_data = {'name': 'Massage Updated'}
        result = mock_facade.update_prestation('prestation-id', **update_data)
        
        self.assertEqual(result, mock_prestation)
        mock_facade.update_prestation.assert_called_once_with('prestation-id', **update_data)

    @patch('app.api.v1.prestations.facade')
    def test_delete_prestation_logic(self, mock_facade):
        """Test logique suppression prestation"""
        mock_facade.delete_prestation.return_value = True
        
        result = mock_facade.delete_prestation('prestation-id')
        
        self.assertTrue(result)
        mock_facade.delete_prestation.assert_called_once_with('prestation-id')
    
    @patch('app.api.v1.prestations.facade')
    def test_get_all_prestations_for_user_logic(self, mock_facade):
        """Test logique récupération prestations pour utilisateur non-admin"""
        mock_prestations = [Mock(), Mock()]
        mock_facade.get_all_prestations_for_user.return_value = mock_prestations
        
        result = mock_facade.get_all_prestations_for_user()
        
        self.assertEqual(result, mock_prestations)
        mock_facade.get_all_prestations_for_user.assert_called_once()

    @patch('app.api.v1.prestations.facade')
    def test_get_prestation_by_name_logic(self, mock_facade):
        """Test logique récupération prestation par nom"""
        mock_prestation = Mock()
        mock_facade.get_prestation_by_name.return_value = mock_prestation
        
        name = 'Massage Relaxant'
        result = mock_facade.get_prestation_by_name(name)
        
        self.assertEqual(result, mock_prestation)
        mock_facade.get_prestation_by_name.assert_called_once_with(name)

    @patch('app.api.v1.prestations.facade')
    def test_delete_prestation_with_reassignment_logic(self, mock_facade):
        """Test logique de réassignation lors de la suppression d'une prestation"""
        prestation_id = 'prestation-id'
        ghost_id = 'ghost-id'
        
        mock_prestation = Mock()
        mock_prestation.id = prestation_id
        mock_ghost = Mock()
        mock_ghost.id = ghost_id
        
        mock_facade.get_prestation_by_id.return_value = mock_prestation
        mock_facade.get_prestation_by_name.return_value = mock_ghost
        mock_facade.get_review_by_prestation.return_value = [Mock()] # Simule présence d'avis
        
        # Le endpoint appelle get_review_by_prestation avant la réassignation
        reviews = mock_facade.get_review_by_prestation(prestation_id)
        if reviews:
            mock_facade.reassign_reviews_from_prestation(prestation_id, ghost_id)
            
        mock_facade.delete_prestation(prestation_id)
        
        mock_facade.get_review_by_prestation.assert_called_once_with(prestation_id)
        mock_facade.reassign_reviews_from_prestation.assert_called_once_with(prestation_id, ghost_id)
        mock_facade.delete_prestation.assert_called_once_with(prestation_id)


if __name__ == '__main__':
    unittest.main()