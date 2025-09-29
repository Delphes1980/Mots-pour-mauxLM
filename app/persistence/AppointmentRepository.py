from sqlalchemy.exc import SQLAlchemyError
from app.models.appointment import Appointment
from app.persistence.BaseRepository import BaseRepository
from app.models.baseEntity import strlen_validation

class AppointmentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Appointment)

    def create_appointment(self, message, user, prestation):
        try:
            # Vérifier si la prestation existe
            if not prestation:
                raise ValueError("La prestation spécifiée n'existe pas")
            # Vérifier la longeur du message
            strlen_validation(message, "Message", 10, 500)
            
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
        
    def get_by_user_id(self, user_id):
        return self.db.session.query(self.model_class).filter_by(_user_id=user_id).first()
    
    def get_by_prestation_id(self, prestation_id):
        return self.db.session.query(self.model_class).filter_by(_prestation_id=prestation_id).all()
    
    def get_by_user_and_prestation(self, user_id, prestation_id):
        """Récupérer un rendez-vous par utilisateur et prestation"""
        return self.db.session.query(self.model_class).filter_by(
            _user_id=user_id, 
            _prestation_id=prestation_id
        ).first()
        