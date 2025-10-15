import os
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv("app/.env.dev")


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    ERROR_INCLUDE_MESSAGE = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in ['true', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_RECIPIENT_PRACTITIONER = os.getenv('MAIL_RECIPIENT_PRACTITIONER')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Configuration des cookies
    JWT_TOKEN_LOCATION = ['cookies']  # Définir le type de stockage des tokens
    JWT_COOKIE_HTTPONLY = True  # Rendre les cookies HTTP seulement, rend le cookie inacessible au JS (protection XSS)
    JWT_COOKIE_SAMESITE = 'Lax'  # Le cookie est renvoyé seulement pour le même site
    JWT_COOKIE_CSRF_PROTECT = False  # Active la protection CSRF pour les cookies
    JWT_ACCESS_CSRF_COOKIE_NAME = 'csrf_access_token'  # Nom du cookie CSRF pour les tokens d'accès (utile pour la détection du token par le front)

class DevelopmentConfig(Config):
    DEBUG = True
    ERROR_INCLUDE_MESSAGE = False
    BCRYPT_LOG_ROUNDS = 4  # Use fewer rounds in development for speed
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_COOKIE_SECURE = False # Sécurité par CSRF désactivée
    FRONTEND_URL = "http://localhost:8000"

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_COOKIE_SECURE = True  # Sécurité CSRF activée
    FRONTEND_URL = "https://www.motspourmauxlm.fr"

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_TEST_URL') + '?client_encoding=utf8'
    BCRYPT_LOG_ROUNDS = 4  # Use fewer rounds for testing to speed up tests
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration JWT pour les tests
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # 15min d'expiration pour les tests
    JWT_COOKIE_SECURE = False  # Sécurité CSRF désactivée
    JWT_COOKIE_CSRF_PROTECT = False  # Désactiver CSRF pour les tests
    JWT_TOKEN_LOCATION = ['cookies']  # Utiliser seulement les cookies comme en production

    # Configuration email spécifique aux tests
    MAIL_RECIPIENT_PRACTITIONER = "test-practitioner@example.com"
    MAIL_USERNAME = "test-sender@example.com"
    MAIL_SERVER = "localhost"
    MAIL_PORT = 587
    MAIL_USE_TLS = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'testing': TestingConfig
}
