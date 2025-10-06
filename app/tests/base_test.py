#!/usr/bin/env python3
"""
Classe de base pour tous les tests avec PostgreSQL
=================================================

Cette classe configure automatiquement :
- Flask application avec contexte de test
- SQLAlchemy avec base de données therapie_test
- Création/suppression des tables pour chaque test
- Isolation des tests avec rollback de transactions

Utilise la base de données: therapie_test
"""

import unittest
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api

# Import de l'instance db depuis app
from app import db, mail

# Import de tous les modèles pour éviter les erreurs de relations
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.appointment import Appointment
from app.config import TestingConfig

class BaseTest(unittest.TestCase):
    """Classe de base pour tous les tests utilisant PostgreSQL"""
    
    @classmethod
    def setUpClass(cls):
        """Configuration une seule fois pour toute la classe de test"""
        os.environ['FLASK_ENV'] = 'testing'
        
        # Création de l'application Flask pour les tests
        cls.app = Flask(__name__)
        cls.app.config.from_object(TestingConfig)
        
        # Utiliser l'instance db existante
        cls.db = db
        cls.db.init_app(cls.app)
        
        # Initialiser Flask-Mail
        mail.init_app(cls.app)
        
        # Initialiser JWT Manager
        jwt = JWTManager(cls.app)
        
        # Contexte d'application
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Compteur pour éviter les conflits d'API
        cls._api_counter = 0
        
        # Création des tables
        # Forcer l'enregistrement des modèles
        User.__table__
        # Créer les tables avec metadata
        User.metadata.create_all(cls.db.engine)
        # Puis db.create_all()
        cls.db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        """Nettoyage après tous les tests de la classe"""
        cls.db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        """Configuration avant chaque test individuel"""
        # Supprimer et recréer toutes les tables pour avoir le schéma à jour
        self.db.drop_all()
        self.db.create_all()
    
    def tearDown(self):
        """Nettoyage après chaque test individuel"""
        # Supprimer toutes les données des tables
        self.db.session.query(Appointment).delete()
        self.db.session.query(Review).delete()
        self.db.session.query(User).delete()
        self.db.session.query(Prestation).delete()
        self.db.session.commit()
    
    def save_to_db(self, *objects):
        """Méthode utilitaire pour sauvegarder des objets en DB"""
        for obj in objects:
            self.db.session.add(obj)
        self.db.session.commit()
    
    def delete_from_db(self, *objects):
        """Méthode utilitaire pour supprimer des objets de la DB"""
        for obj in objects:
            self.db.session.delete(obj)
        self.db.session.commit()
    
    def create_test_api(self, title_suffix=''):
        """Créer une API de test unique pour éviter les conflits d'endpoints"""
        from flask_jwt_extended import JWTManager
        
        self.__class__._api_counter += 1
        
        # Créer une nouvelle app Flask pour chaque API de test
        test_app = Flask(f'test_app_{self.__class__._api_counter}')
        test_app.config.from_object(TestingConfig)
        
        # Initialiser les extensions sur la nouvelle app
        self.db.init_app(test_app)
        mail.init_app(test_app)
        jwt = JWTManager(test_app)
        
        # Créer l'API sur la nouvelle app
        api = Api(
            test_app,
            version='1.0', 
            title=f'Test API {self.__class__._api_counter} {title_suffix}'.strip(),
            doc=False
        )
        
        # Remplacer l'app principale par la nouvelle pour ce test
        self.app = test_app
        
        return api