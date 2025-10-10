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
        JWTManager(cls.app)
        
        # Contexte d'application
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Compteur pour éviter les conflits d'API
        cls._api_counter = 0
        
        # Test de connexion à la base de données
        try:
            cls.db.engine.connect()
            print("✅ Connexion à la base réussie")
        except Exception as e:
            print("❌ Connexion échouée :", str(e))
            raise
        
        # Créer le schéma une seule fois
        try:
            print("🔍 URI utilisée :", repr(cls.app.config["SQLALCHEMY_DATABASE_URI"]))

            cls.db.create_all()
        except UnicodeDecodeError:
            # Erreur UTF-8 détectée, forcer la recréation de l'engine
            cls.db.engine.dispose()
            # Recréer une nouvelle app Flask
            new_app = Flask(f'{cls.__name__}_recovery')
            new_app.config.from_object(TestingConfig)
            cls.db.init_app(new_app)
            mail.init_app(new_app)
            JWTManager(new_app)
            cls.app_context.pop()
            cls.app = new_app
            cls.app_context = new_app.app_context()
            cls.app_context.push()
            cls.db.create_all()
    
    @classmethod
    def tearDownClass(cls):
        """Nettoyage après tous les tests de la classe"""
        try:
            cls.db.session.remove()
            cls.db.drop_all()
        except Exception:
            pass  # Ignorer les erreurs de nettoyage
        finally:
            if hasattr(cls, 'app_context'):
                cls.app_context.pop()
    
    def setUp(self):
        """Nettoyage des données avant chaque test"""
        print(f"🔄 Nettoyage avant test : {self.__class__.__name__}")
        self.db.session.rollback()
        try:
            # Supprimer dans l'ordre des dépendances (enfants d'abord)
            for model in [Appointment, Review, Prestation, User]:
                self.db.session.query(model).delete()
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            self.db.drop_all()
            self.db.create_all()
        self.db.session.expire_all()
    
    def tearDown(self):
        """Rollback pour garantir l'isolation"""
        self.db.session.rollback()
    
    def save_to_db(self, *objects):
        """Méthode utilitaire pour sauvegarder des objets en DB"""
        for obj in objects:
            print(f"💾 Sauvegarde en base : {obj.__class__.__name__} → {getattr(obj, 'email', obj)}")
            self.db.session.add(obj)
        self.db.session.commit()
    
    def delete_from_db(self, *objects):
        """Méthode utilitaire pour supprimer des objets de la DB"""
        for obj in objects:
            self.db.session.delete(obj)
        self.db.session.commit()
    
    def create_admin_user(self):
        """Créer un utilisateur admin pour les tests"""
        admin = User(
            email="admin@therapie.fr",
            password="Password123!",
            first_name="Admin",
            last_name="Test",
            is_admin=True
        )
        self.save_to_db(admin)
        return admin
    
    def create_test_api(self, title_suffix=''):
        """Créer une API de test unique pour éviter les conflits d'endpoints"""
        if not hasattr(self.__class__, '_api_counter'):
            self.__class__._api_counter = 0
        self.__class__._api_counter += 1
        
        # Créer une nouvelle app Flask pour chaque API de test
        test_app = Flask(f'test_app_{self.__class__._api_counter}')
        test_app.config.from_object(TestingConfig)
        
        # Initialiser les extensions sur la nouvelle app
        self.db.init_app(test_app)
        mail.init_app(test_app)
        JWTManager(test_app)
        
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