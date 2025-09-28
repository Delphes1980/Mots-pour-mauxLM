from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User
from app.persistence.BaseRepository import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def create_user(self, first_name, last_name, email, password, address=None, phone_number=None, is_admin=False):
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = self.get_by_email(email)
            if existing_user:
                raise ValueError("Un utilisateur avec cet email existe déjà.")

            # Créer un nouvel utilisateur
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                address=address,
                phone_number=phone_number,
                is_admin=is_admin
            )
            self.db.session.add(new_user)
            self.db.session.commit()
            return new_user
        except SQLAlchemyError:
            raise ValueError("Erreur lors de la création de l'utilisateur.")

    def get_by_email(self, email):
        return self.db.session.query(self.model_class).filter_by(email=email).first()