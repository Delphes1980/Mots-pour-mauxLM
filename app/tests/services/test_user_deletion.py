import json
import unittest
from flask_jwt_extended import create_access_token

# Import des modèles et services nécessaires
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review # Ajout pour les vérifications directes de la base
from app.services.UserService import UserService
from app.services.ReviewService import ReviewService
from app import db
from app.tests.base_test import BaseTest

class TestUserDeletion(BaseTest):

    def setUp(self):
        super().setUp()
        
        # Instanciation du service User pour l'utiliser dans les tests
        self.user_service = UserService() 

        # 1. Utilisation de get_by_attribute du repository d'utilisateur pour récupérer le ghost_user
        ghost_email = "deleted@system.local"
        
        # On passe par le repository du UserService pour rester cohérent avec l'architecture
        ghost = self.user_service.user_repository.get_by_attribute("email", ghost_email)

        if not ghost:
            # Si l'utilisateur n'existe pas, on le crée
            ghost = User(
                first_name="Ghost",
                last_name="User",
                email=ghost_email,
                password="GhostUser#2025!",
                address="N/A",
                phone_number="0000000000",
                is_admin=False
            )
            self.save_to_db(ghost)
        
        # Stockage de l'utilisateur fantôme dans la classe de test
        self.ghost_user = ghost

    def test_delete_user_with_reviews(self):
        # On utilise l'utilisateur fantôme récupéré/créé dans setUp
        ghost_user = self.ghost_user 

        # Créer un utilisateur normal
        user = User(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            password="Password123!",
            address="1 rue des Lilas",
            phone_number="0601020304",
            is_admin=False
        )
        self.save_to_db(user)

        # Créer deux prestations distinctes
        prestation1 = Prestation(name="Massage relaxant")
        prestation2 = Prestation(name="Massage tonique")
        self.save_to_db(prestation1, prestation2)

        # Préparation du ReviewService (nécessite l'accès à la DB de test)
        review_service = ReviewService()
        review_service.review_repository.db = self.db
        review_service.user_repository.db = self.db
        review_service.prestation_repository.db = self.db

        review_data_1 = {
            "text": "Très bon service",
            "rating": 5,
            "user_id": user.id,
            "prestation_id": prestation1.id
        }
        review_data_2 = {
            "text": "Accueil chaleureux",
            "rating": 4,
            "user_id": user.id,
            "prestation_id": prestation2.id
        }

        review1 = review_service.create_review(**review_data_1)
        review2 = review_service.create_review(**review_data_2)

        # Vérifier que les reviews sont bien liées
        reviews_before = review_service.review_repository.get_by_user_id(user.id)
        assert len(reviews_before) == 2

        # Supprimer l'utilisateur via le UserService
        result = self.user_service.delete_user(user.id)
        assert result is True

        # Vérifier que l'utilisateur a été supprimé
        deleted_user = db.session.query(User).filter_by(id=user.id).first()
        assert deleted_user is None

        # Vérifier que les reviews ont été réassignées au ghost_user
        reassigned_reviews = db.session.query(Review).filter_by(user_id=ghost_user.id).all()
        assert len(reassigned_reviews) == 2

    def test_delete_user_without_reviews(self):
        # On utilise l'utilisateur fantôme récupéré/créé dans setUp
        ghost_user = self.ghost_user 

        # Créer un utilisateur sans avis
        user = User(
            first_name="Claire",
            last_name="Martin",
            email="claire.martin@example.com",
            password="Password456!",
            address="2 avenue des Champs",
            phone_number="0605060708",
            is_admin=False
        )
        self.save_to_db(user)

        # Vérifier qu'il n'a pas de reviews
        reviews_before = db.session.query(User).filter_by(id=user.id).first().reviews
        assert len(reviews_before) == 0

        # Supprimer l'utilisateur via le UserService
        result = self.user_service.delete_user(user.id)
        assert result is True

        # Vérifier que l'utilisateur a été supprimé
        deleted_user = db.session.query(User).filter_by(id=user.id).first()
        assert deleted_user is None

        # Vérifier qu'aucune review n'a été réassignée
        # On vérifie directement les reviews associées au ghost_user
        reassigned_reviews = db.session.query(User).filter_by(id=ghost_user.id).first().reviews
        assert len(reassigned_reviews) == 0
