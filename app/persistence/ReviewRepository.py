from sqlalchemy.exc import SQLAlchemyError
from app.models.review import Review
from app.persistence.BaseRepository import BaseRepository
from app.utils import (CustomError, rating_validation, type_validation, text_field_validation, is_valid_uuid4)
from app.models.user import User
from app.models.prestation import Prestation
from sqlalchemy.orm import joinedload


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
            self.db.session.rollback()
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

    def reassign_reviews_from_user(self, old_user_id, new_user_id):
        """Réassigner les avis d'un utilisateur supprimé à un utilisateur fantôme, pour conserver les avis"""
        # Vérifier la validité des identifiants
        if not is_valid_uuid4(old_user_id):
            raise ValueError("Format d'identifiant utilisateur à supprimer non valide")
        if not is_valid_uuid4(new_user_id):
            raise ValueError("Format d'identifiant utilisateur fantôme non valide")

        # Vérifier que les utilisateurs existent
        old_user = self.db.session.query(User).get(old_user_id)
        new_user = self.db.session.query(User).get(new_user_id)

        if not old_user:
            raise ValueError("L'utilisateur à supprimer n'a pas été trouvé")
        if not new_user:
            raise ValueError("Le nouvel utilisateur n'a pas été trouvé")
        
        # Vérifier s'il y a des avis à réassigner
        reviews = self.get_by_user_id(old_user_id)
        if not reviews:
            return 0

        # Réassigner les avis
        for review in reviews:
            review.user= new_user
        self.db.session.commit()

        return len(reviews)

    def reassign_reviews_from_prestation(self, old_prestation_id, new_prestation_id):
        """Réassigner les avis d'une prestation supprimée à une prestation fantôme, pour conserver les avis"""
        # Vérifier la validité des identifiants
        if not is_valid_uuid4(old_prestation_id):
            raise ValueError("Format d'identifiant prestation à supprimer non valide")
        if not is_valid_uuid4(new_prestation_id):
            raise ValueError("Format d'identifiant prestation fantôme non valide")

        # Vérifier que les prestations existent
        old_prestation = self.db.session.query(Prestation).get(old_prestation_id)
        new_prestation = self.db.session.query(Prestation).get(new_prestation_id)

        if not old_prestation:
            raise ValueError("La prestation à supprimer n'a pas été trouvée")
        if not new_prestation:
            raise ValueError("La nouvelle prestation n'a pas été trouvée")
        
        # Vérifier s'il y a des avis à réassigner
        reviews = self.get_by_prestation_id(old_prestation_id)
        if not reviews:
            return 0

        # Réassigner les avis
        for review in reviews:
            review.prestation_id= new_prestation_id
        self.db.session.commit()

        return len(reviews)
    
    def get_all_public_reviews(self):
        """Récupérer tous les commentaires publics"""
        try:
            reviews = self.db.session.query(Review).options(joinedload(Review._user), joinedload(Review._prestation)).all()
            return reviews
        
        except Exception as e:
            raise CustomError(f"Erreur lors de la récupération des commentaires publics : {str(e)}")
