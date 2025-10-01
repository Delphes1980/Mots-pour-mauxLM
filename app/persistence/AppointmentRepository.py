from sqlalchemy.exc import SQLAlchemyError
from app.models.appointment import Appointment
from app.persistence.BaseRepository import BaseRepository
from app.utils import (text_field_validation, type_validation, is_valid_uuid4)
from app.models.user import User
from app.models.prestation import Prestation


class AppointmentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Appointment)

    def create(self, **kwargs):
        """Utilise create_appointment() avec validations au lieu de create() dans BaseRepository"""
        return self.create_appointment(
            kwargs.get('message'),
            kwargs.get('user'),
            kwargs.get('prestation')
        )

    def create_appointment(self, message, user, prestation):
        try:
            # Vérifier si la prestation existe
            if not prestation:
                raise ValueError("La prestation spécifiée n'existe pas")
            type_validation(prestation, 'prestation', Prestation)
            if not is_valid_uuid4(prestation.id):
                raise ValueError("Format d'identifiant de prestation invalide")

            # Vérifier la longueur du message
            text_field_validation(message, 'message', 1, 500)

            # Vérifier l'utilisateur
            if not user:
                raise ValueError("L'utilisateur spécifié n'existe pas")
            type_validation(user, 'user', User)
            if not is_valid_uuid4(user.id):
                raise ValueError("Format d'identifiant utilisateur invalide")

            # Créer un nouveau rendez-vous
            new_appointment = Appointment(
                message=message, 
                user=user,
                prestation=prestation
            )
            self.db.session.add(new_appointment)
            self.db.session.commit()
            return new_appointment
        except SQLAlchemyError:
            raise ValueError("Erreur lors de la création du rendez-vous")

    def get_by_user_and_prestation(self, user_id, prestation_id):
        """Récupérer un rendez-vous par utilisateur et prestation"""
        return self.db.session.query(self.model_class).filter_by(
            _user_id=user_id, 
            _prestation_id=prestation_id
        ).first()
