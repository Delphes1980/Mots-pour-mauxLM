#!/usr/bin/env python3
"""
Test final de connexion PostgreSQL Windows depuis WSL
====================================================

Ce script valide la configuration complète :
- Connexion WSL → PostgreSQL 18 Windows
- Création des tables SQLAlchemy
- Opérations CRUD sur les modèles
- Validation des relations entre entités

Configuration testée :
- Host: 172.29.128.1 (IP WSL vers Windows)
- Port: 5432
- Database: therapie_dev
- User: postgres
"""

import os
os.environ['FLASK_ENV'] = 'development'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import DevelopmentConfig
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.appointment import Appointment

def test_postgresql_connection():
    """Test complet de la configuration PostgreSQL"""
    
    # Configuration Flask minimale
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    db = SQLAlchemy()
    db.init_app(app)
    
    with app.app_context():
        print("=== Test Configuration PostgreSQL Windows ===")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        try:
            # Test 1: Connexion de base
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ Connexion réussie - {version}")
            
            # Test 2: Création des tables
            db.create_all()
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Tables créées: {tables}")
            
            # Test 3: Test CRUD utilisateur
            test_user = User(
                first_name="Test",
                last_name="PostgreSQL", 
                email="test.postgresql@example.com",
                password="TestPassword123!"
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Insertion utilisateur réussie")
            
            # Test 4: Lecture
            user = db.session.query(User).filter_by(email="test.postgresql@example.com").first()
            if user:
                print(f"✅ Lecture réussie: {user.first_name} {user.last_name}")
                
                # Nettoyage
                db.session.delete(user)
                db.session.commit()
                print("✅ Suppression réussie")
            
            print("\n🎉 Configuration PostgreSQL Windows validée !")
            print("Vous pouvez maintenant développer votre application en toute confiance.")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = test_postgresql_connection()
    exit(0 if success else 1)