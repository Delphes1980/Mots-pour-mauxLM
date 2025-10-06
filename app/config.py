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
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_RECIPIENT_PRACTITIONER = os.getenv('MAIL_RECIPIENT_PRACTITIONER')

class DevelopmentConfig(Config):
    DEBUG = True
    ERROR_INCLUDE_MESSAGE = False
    BCRYPT_LOG_ROUNDS = 4  # Use fewer rounds in development for speed
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_TEST_URL')
    BCRYPT_LOG_ROUNDS = 4  # Use fewer rounds for testing to speed up tests
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration JWT pour les tests
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # 15min d'expiration pour les tests
    
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
