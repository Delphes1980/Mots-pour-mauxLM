from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User
from app.persistence.BaseRepository import BaseRepository
from app.utils import (name_validation, email_validation, validate_password, address_validation, validate_phone_number)


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def create(self, **kwargs):
        """Utilise create_user() avec validations au lieu de create() dans BaseRepository"""
        return self.create_user(
            kwargs.get('first_name'),
            kwargs.get('last_name'),
            kwargs.get('email'),
            kwargs.get('password'),
            kwargs.get('address'),
            kwargs.get('phone_number'),
            kwargs.get('is_admin', False)
        )

    def create_user(self, first_name, last_name, email, password, address=None, phone_number=None, is_admin=False):
        try:
            # Valider les données
            first_name = name_validation(first_name, 'first_name')
            last_name = name_validation(last_name, 'last_name')
            email = email_validation(email)
            password = validate_password(password)
            address = address_validation(address)
            phone_number = validate_phone_number(phone_number)

            # Vérifier si l'utilisateur existe déjà
            existing_user = self.get_by_attribute("email", email)
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
            self.db.session.rollback()
            raise ValueError("Erreur lors de la création de l'utilisateur.")

    def search_by_email_fragment(self, fragment):
        """Recherche des utilisateurs dont l'email contient le fragment"""
        try:
            return self.db.session.query(User).filter(User.email.ilike(f'%{fragment}%')).all()
        except SQLAlchemyError:
            self.db.session.rollback()
            raise ValueError("Erreur lors de la recherche d'utilisateur par email.")
