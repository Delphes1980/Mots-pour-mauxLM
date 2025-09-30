from sqlalchemy.exc import SQLAlchemyError
from app.models.review import Review
from app.persistence.BaseRepository import BaseRepository
from app.utils import (rating_validation, type_validation, strlen_validation)
from app.models.user import User

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
            type_validation(text, 'text', str)
            strlen_validation(text, 'text', 2, 500)

            # Vérifier si la prestation existe
            if not prestation:
                raise ValueError("La prestation spécifiée n'existe pas.")

            # Vérifier l'utilisateur
            if not user:
                raise ValueError("L'utilisateur spécifié n'existe pas")
            type_validation(user, 'user', User)

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
        """Récupérer un avis par utilisateur et prestation"""
        return self.db.session.query(self.model_class).filter_by(
            _user_id=user_id, 
            _prestation_id=prestation_id
        ).first()
