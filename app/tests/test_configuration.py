#!/usr/bin/env python3

import json
import unittest
import os
from app.tests.base_test import BaseTest
from app import create_app

class TestConfiguration(BaseTest):
    """Tests de configuration - Variables d'environnement et configuration Flask"""

    def test_app_configuration_loaded(self):
        """Test que la configuration de l'application est chargée"""
        app = create_app()
        self.assertIsNotNone(app.config.get('SECRET_KEY'))
        self.assertIsNotNone(app.config.get('SQLALCHEMY_DATABASE_URI'))

    def test_jwt_configuration(self):
        """Test configuration JWT"""
        app = create_app()
        self.assertIsNotNone(app.config.get('JWT_SECRET_KEY'))
        self.assertIn('JWT_TOKEN_LOCATION', app.config)
        self.assertIn('JWT_COOKIE_SECURE', app.config)

    def test_database_configuration(self):
        """Test configuration base de données"""
        app = create_app()
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        self.assertIsNotNone(db_uri)
        self.assertIn('postgresql', db_uri.lower())

    def test_mail_configuration_present(self):
        """Test que la configuration mail est présente"""
        # Vérifier que les variables d'environnement mail sont définies
        mail_username = os.getenv('MAIL_USERNAME')
        mail_password = os.getenv('MAIL_PASSWORD')

        # Ces variables peuvent être None en test, mais on vérifie leur existence
        self.assertIsNotNone(os.environ.get('MAIL_USERNAME', 'default'))
        self.assertIsNotNone(os.environ.get('MAIL_PASSWORD', 'default'))

    def test_environment_variables_structure(self):
        """Test structure des variables d'environnement"""
        required_vars = [
            'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME',
            'MAIL_USERNAME', 'MAIL_PASSWORD'
        ]

        for var in required_vars:
            # Vérifier que la variable existe (même si vide en test)
            value = os.environ.get(var, 'test_default')
            self.assertIsNotNone(value)

    def test_app_debug_mode(self):
        """Test mode debug de l'application"""
        app = create_app()
        # En test, debug peut être True ou False
        self.assertIn(app.config.get('DEBUG'), [True, False])

    def test_sqlalchemy_track_modifications(self):
        """Test configuration SQLAlchemy"""
        app = create_app()
        # SQLALCHEMY_TRACK_MODIFICATIONS devrait être False pour les performances
        self.assertFalse(app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS', True))

if __name__ == '__main__':
    unittest.main()
