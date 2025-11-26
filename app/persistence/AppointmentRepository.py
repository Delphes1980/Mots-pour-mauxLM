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
                user=user,
                message=message,
                prestation=prestation
            )
            self.db.session.add(new_appointment)
            self.db.session.commit()
            return new_appointment
        except SQLAlchemyError:
            self.db.session.rollback()
            raise ValueError("Erreur lors de la création du rendez-vous")

    def get_by_user_and_prestation(self, user_id, prestation_id):
        """Récupérer les rendez-vous par utilisateur et prestation"""
        return self.db.session.query(self.model_class).filter_by(
            _user_id=user_id, 
            _prestation_id=prestation_id
        ).all()

    def get_by_prestation_id(self, prestation_id):
        """Récupérer les rendez-vous par prestation"""
        return self.db.session.query(self.model_class).filter_by(
            _prestation_id=prestation_id
        ).all()

    def get_by_user_id(self, user_id):
        """Récupérer les rendez-vous par utilisateur"""
        return self.db.session.query(self.model_class).filter_by(
            _user_id=user_id
        ).all()

    def reassign_appointments_from_user(self, old_user_id, new_user_id):
        """Réassigner les rendez-vous d'un utilisateur supprimé à un utilisateur fantôme, pour pouvoir supprimer l'utilisateur"""
        # Vérifier la validité des identifiants
        if not is_valid_uuid4(old_user_id):
            raise ValueError('Format d\'identifiant utilisateur à supprimer non valide')
        if not is_valid_uuid4(new_user_id):
            raise ValueError('Format d\'identifiant utilisateur fantôme non valide')

        # Vérifier que les utilisateurs existent
        old_user = self.db.session.query(User).get(old_user_id)
        new_user = self.db.session.query(User).get(new_user_id)

        if not old_user:
            raise ValueError('L\'utilisateur à supprimer n\'a pas été trouvé')
        if not new_user:
            raise ValueError('Le nouvel utilisateur n\'a pas été trouvé')

        # Vérifier s'il y a des rendez-vous à réassigner
        appointments = self.get_by_user_id(old_user_id)
        if not appointments:
            return 0

        # Réassigner les rendez-vous
        for appointment in appointments:
            appointment.user = new_user
        self.db.session.commit()

        return len(appointments)
