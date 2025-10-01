from sqlalchemy.exc import SQLAlchemyError
from app.models.review import Review
from app.persistence.BaseRepository import BaseRepository
from app.utils import (rating_validation, type_validation, text_field_validation, is_valid_uuid4)
from app.models.user import User
from app.models.prestation import Prestation


class ReviewRepository(BaseRepository):
    def __init__(self):
        super().__init__(Review)

    def create(self, **kwargs):
        """Utilise create_review() avec validations au lieu de create() dans BaseRepository"""
        return self.create_review(
            kwargs.get('text'),
            kwargs.get('rating'),
            kwargs.get('user'),
            kwargs.get('prestation')
        )
        
    def create_review(self, text, rating, user, prestation):
        try:
            # Valider la notation
            rating_validation(rating)

            # Valider le texte
            text_field_validation(text, 'text', 2, 500)

            # Vérifier la prestation
            if not prestation:
                raise ValueError("La prestation spécifiée n'existe pas.")
            type_validation(prestation, 'prestation', Prestation)
            if not is_valid_uuid4(prestation.id):
                raise ValueError("Format d'identifiant de prestation invalide")

            # Vérifier l'utilisateur
            if not user:
                raise ValueError("L'utilisateur spécifié n'existe pas")
            type_validation(user, 'user', User)
            if not is_valid_uuid4(user.id):
                raise ValueError("Format d'identifiant utilisateur invalide")

            # Vérifier si le commentaire existe déjà pour cette prestation
            existing_review = self.get_by_user_and_prestation(user.id, prestation.id)
            if existing_review:
                raise ValueError("Un commentaire existe déjà pour cette prestation.")

            # Créer un nouveau commentaire
            new_review = Review(
                text=text,
                rating=rating,
                user=user,
                prestation=prestation
            )
            self.db.session.add(new_review)
            self.db.session.commit()
            return new_review
        except SQLAlchemyError:
            raise ValueError("Erreur lors de la création du commentaire")

    def get_by_user_and_prestation(self, user_id, prestation_id):
        """Récupérer l'avis par utilisateur et prestation (un seul par type de prestation)"""
        return self.db.session.query(self.model_class).filter_by(
            _user_id=user_id, 
            _prestation_id=prestation_id
        ).first()

    def get_by_prestation_id(self, prestation_id):
        """Récupérer les avis par prestation"""
        return self.db.session.query(self.model_class).filter_by(
            _prestation_id=prestation_id
        ).all()

    def get_by_user_id(self, user_id):
        """Récupérer les avis par utilisateur"""
        return self.db.session.query(self.model_class).filter_by(
            _user_id=user_id
        ).all()
