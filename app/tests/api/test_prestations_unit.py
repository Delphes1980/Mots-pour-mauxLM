#!/usr/bin/env python3

import json
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_restx import Api
from flask_jwt_extended import create_access_token

from app.tests.base_test import BaseTest
from app.api.v1.prestations import api as prestations_api
from app.models.user import User
from app.utils import CustomError


class TestPrestationsUnit(BaseTest):
    """Tests unitaires pour l'API prestations avec mocks"""
    
    def setUp(self):
        super().setUp()
        
        # Configuration de l'API via BaseTest
        self.api = self.create_test_api('Unit')
        self.api.add_namespace(prestations_api, path='/prestations')
        
        # Client de test
        self.client = self.app.test_client()
        
        # Créer utilisateurs
        self.admin_user = User(
            email='admin@test.com',
            password='Password123!',
            first_name='Admin',
            last_name='Test',
            is_admin=True
        )
        self.regular_user = User(
            email='user@test.com',
            password='Password123!',
            first_name='User',
            last_name='Test',
            is_admin=False
        )
        self.save_to_db(self.admin_user, self.regular_user)
        
        # Tokens JWT
        with self.app.app_context():
            self.admin_token = create_access_token(
                identity=str(self.admin_user.id),
                additional_claims={'is_admin': True}
            )
            self.user_token = create_access_token(
                identity=str(self.regular_user.id),
                additional_claims={'is_admin': False}
            )
    
    def get_auth_headers(self, token):
        return {'Authorization': f'Bearer {token}'}
    
    @patch('app.services.facade.Facade.create_prestation')
    def test_create_prestation_facade_called(self, mock_create):
        """Test que facade.create_prestation est appelé correctement"""
        mock_prestation = MagicMock()
        mock_prestation.id = 'test-id'
        mock_prestation.name = 'Massage'
        mock_create.return_value = mock_prestation
        
        data = {'name': 'Massage'}
        response = self.client.post(
            '/prestations/',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_once_with(name='Massage')
    
    @patch('app.services.facade.Facade.create_prestation')
    def test_create_prestation_custom_error_handling(self, mock_create):
        """Test gestion CustomError lors de la création"""
        mock_create.side_effect = CustomError('Prestation existe déjà', 409)
        
        data = {'name': 'Massage'}
        response = self.client.post(
            '/prestations/',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 409)
    
    @patch('app.services.facade.Facade.create_prestation')
    def test_create_prestation_exception_handling(self, mock_create):
        """Test gestion Exception générale"""
        mock_create.side_effect = Exception('Erreur inattendue')
        
        data = {'name': 'Massage'}
        response = self.client.post(
            '/prestations/',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 400)
    
    @patch('app.services.facade.Facade.create_prestation')
    def test_create_prestation_none_result(self, mock_create):
        """Test quand facade retourne None"""
        mock_create.return_value = None
        
        data = {'name': 'Massage'}
        response = self.client.post(
            '/prestations/',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 500)
    
    @patch('app.services.facade.Facade.get_all_prestations')
    def test_get_all_prestations_facade_called(self, mock_get_all):
        """Test que facade.get_all_prestations est appelé"""
        mock_prestations = [
            MagicMock(id='1', name='Massage'),
            MagicMock(id='2', name='Thérapie')
        ]
        mock_get_all.return_value = mock_prestations
        
        response = self.client.get(
            '/prestations/',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        mock_get_all.assert_called_once()
    
    @patch('app.services.facade.Facade.get_prestation_by_name')
    def test_search_prestation_facade_called(self, mock_get_by_name):
        """Test que facade.get_prestation_by_name est appelé avec bon paramètre"""
        mock_prestation = MagicMock(id='1', name='Massage')
        mock_get_by_name.return_value = mock_prestation
        
        response = self.client.get(
            '/prestations/search?name=Massage',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        mock_get_by_name.assert_called_once_with('Massage')
    
    @patch('app.services.facade.Facade.get_prestation_by_name')
    def test_search_prestation_not_found_handling(self, mock_get_by_name):
        """Test gestion prestation non trouvée"""
        mock_get_by_name.side_effect = CustomError('Prestation non trouvée', 404)
        
        response = self.client.get(
            '/prestations/search?name=Inexistant',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_search_prestation_missing_name_parameter(self):
        """Test paramètre name manquant"""
        response = self.client.get(
            '/prestations/search',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 400)
    
    @patch('app.services.facade.Facade.get_prestation_by_id')
    def test_get_prestation_by_id_facade_called(self, mock_get_by_id):
        """Test que facade.get_prestation_by_id est appelé avec bon ID"""
        mock_prestation = MagicMock(id='test-id', name='Massage')
        mock_get_by_id.return_value = mock_prestation
        
        response = self.client.get(
            '/prestations/test-id',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        mock_get_by_id.assert_called_once_with('test-id')
    
    @patch('app.services.facade.Facade.update_prestation')
    def test_update_prestation_facade_called(self, mock_update):
        """Test que facade.update_prestation est appelé correctement"""
        mock_prestation = MagicMock(id='test-id', name='Massage Relaxant')
        mock_update.return_value = mock_prestation
        
        data = {'name': 'Massage Relaxant'}
        response = self.client.put(
            '/prestations/test-id',
            data=json.dumps(data),
            content_type='application/json',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        mock_update.assert_called_once_with('test-id', name='Massage Relaxant')
    
    @patch('app.services.facade.Facade.delete_prestation')
    def test_delete_prestation_facade_called(self, mock_delete):
        """Test que facade.delete_prestation est appelé avec bon ID"""
        mock_delete.return_value = None
        
        response = self.client.delete(
            '/prestations/test-id',
            headers=self.get_auth_headers(self.admin_token)
        )
        
        self.assertEqual(response.status_code, 200)
        mock_delete.assert_called_once_with('test-id')
    
    @patch('app.api.v1.prestations.compare_data_and_model')
    def test_data_validation_called(self, mock_compare):
        """Test que la validation des données est appelée"""
        with patch('app.services.facade.Facade.create_prestation') as mock_create:
            mock_prestation = MagicMock(id='test-id', name='Massage')
            mock_create.return_value = mock_prestation
            
            data = {'name': 'Massage'}
            response = self.client.post(
                '/prestations/',
                data=json.dumps(data),
                content_type='application/json',
                headers=self.get_auth_headers(self.admin_token)
            )
            
            self.assertEqual(response.status_code, 201)
            mock_compare.assert_called_once()


if __name__ == '__main__':
    unittest.main()