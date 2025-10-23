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

from urllib.parse import urlparse, unquote
import psycopg2
import time

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
    _api_counter = 0

    @classmethod
    def setUpClass(cls):
        """Configuration une seule fois pour toute la classe de test avec contournement psycopg2"""
        # 🔒 Neutraliser les variables d'environnement PostgreSQL pour éviter les encodages corrompus
        for var in ["PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD", "PGSERVICE", "PGSERVICEFILE", "PGPASSFILE"]:
            if var in os.environ:
                del os.environ[var]

        os.environ['FLASK_ENV'] = 'testing'

        # --- 1. Création de l'application Flask ---
        cls.app = Flask(__name__)
        cls.app.config.from_object(TestingConfig)

        # --- 2. Récupération et affichage de l'URL de la base ---
        db_url = cls.app.config.get("SQLALCHEMY_DATABASE_URI")
        db_url.encode("utf-8").decode("utf-8")

        # --- 3. Analyse de l'URL pour extraire les paramètres ---
        parsed_url = urlparse(db_url)
        clean_password = unquote(parsed_url.password or "")

        if not clean_password:
            clean_password = os.getenv('DB_PASSWORD')

        db_user = parsed_url.username or "postgres"

        # --- 4. Création manuelle de la connexion psycopg2 ---
        def create_connection():
            db_port = parsed_url.port

            if db_port is None:
                db_port = 5433

            test_host = "localhost"
            
            dsn_string = (
                f"host={test_host} "
                f"port={db_port} "
                f"user={db_user} "
                f"password={clean_password} "
                f"dbname={parsed_url.path.lstrip('/')}"
            )
            return psycopg2.connect(dsn_string)

        # --- 5. Injection du créateur dans SQLAlchemy ---
        cls.app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'creator': create_connection}

        # --- 6. Initialisation des extensions ---
        cls.db = db
        cls.db.init_app(cls.app)
        mail.init_app(cls.app)
        JWTManager(cls.app)

        # --- 7. Contexte d'application ---
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        # --- 8. Création des tables ---
        try:
            cls.db.drop_all()
            cls.db.create_all()
        except UnicodeDecodeError as e:
            cls.db.engine.dispose()

            # Recréation d'une nouvelle app propre
            new_app = Flask(f'{cls.__name__}_recovery')
            new_app.config.from_object(TestingConfig)
            new_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'creator': create_connection}

            cls.db.init_app(new_app)
            mail.init_app(new_app)
            JWTManager(new_app)

            if hasattr(cls, 'app_context'):
                cls.app_context.pop() 

            cls.app = new_app
            cls.app_context = new_app.app_context()
            cls.app_context.push()

            cls.db.create_all()

        # --- 9. Données de base ---
        if hasattr(cls, "insert_initial_data"):
            cls.insert_initial_data()

    
    @classmethod
    def tearDownClass(cls):
        """Nettoyage après tous les tests de la classe"""
        try:
            cls.db.drop_all()
            time.sleep(0.5)
        except Exception as e:
            pass
        finally:
            if hasattr(cls, 'app_context'):
                cls.app_context.pop()

    def setUp(self):
        """
        Configuration avant chaque test : 
        Ouvre une connexion et démarre une transaction pour un Rollback rapide.
        """
        # Le contexte d'application a été créé dans setUpClass
         # RETIRER l'ancienne session scindée pour garantir une table propre
        self.db.session.remove()

        # Ouvre une connexion à partir du pool
        self.connection = self.db.engine.connect()

        # Lie la session de Flask-SQLAlchemy (scoped_session) à notre transaction
        self.db.session.bind = self.connection 

        # Démarre une transaction
        self.transaction = self.connection.begin()
        
        # Créer le client de test Flask
        self.client = self.app.test_client()
    
    def tearDown(self):
        """
        Nettoyage après chaque test : 
        Annule la transaction et ferme la connexion.
        """
        try:
            # 1. Delete data from tables that were populated in setUp.
            # This is critical to clear committed data.
            
            # Delete all users
            self.db.session.query(Appointment).delete()
            self.db.session.query(Review).delete()
            self.db.session.query(User).delete()
            self.db.session.query(Prestation).delete()

            # 2. Commit the deletion to ensure the database is clean.
            self.db.session.commit()

        except Exception as e:
            # Log any errors during cleanup
            self.db.session.rollback()

        finally:
            # Annuler la transaction si elle existe
            if hasattr(self, "transaction"):
                self.transaction.rollback()

            # Fermer la connexion si elle existe
            if hasattr(self, "connection"):
                self.connection.close()

            # Nettoyer la session
            self.db.session.remove()
    
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
        
        # IMPORTANT: Réutiliser l'option de création de connexion psycopg2 définie dans setUpClass
        # C'est crucial pour que la nouvelle app sache comment se connecter à PostgreSQL
        engine_options = self.app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
        if engine_options:
            test_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options

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
