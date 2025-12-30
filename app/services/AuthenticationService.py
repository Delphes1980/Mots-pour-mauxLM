from flask_jwt_extended import create_access_token
from app.persistence.UserRepository import UserRepository
from app.utils import (email_validation, validate_password, verify_password, validate_entity_id, CustomError)


class AuthenticationService:
    def __init__(self):
        self.user_repository = UserRepository()

    def login(self, email, password):
        """Authenticate user with email/password
        
        Args:
            email (str): The user's email address
            password (str): The password provided by the user
            
        Returns:
            The JWT access token
            
        Raises:
            CustomError: if the attributes are invalid(400) or if authentication fails(401)"""
        try:
            email_validation(email)
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        try:
            validate_password(password)
        except ValueError as e:
            raise CustomError("Invalid credentials", 400) from e

        user = self.user_repository.get_by_attribute("email", email)
        if not user or not verify_password(user.password, password):
            raise CustomError("Invalid credentials", 401)

        access_token = create_access_token(
            identity=user.id,
            additional_claims={"is_admin": user.is_admin}
        )
        return access_token

    def change_password(self, user_id, old_password, new_password):
        """Change user password
        
        Args:
            user_id (uuid): The ID of the user
            old_password (str): The user's current password
            new_password (str): The user's new password

        Returns:
            The updated User object

        Raises:
            CustomError: if the data are invalid(400), if the user is not found(404)
        """
        # Valider l'ID de l'utilisateur
        try:
            validate_entity_id(user_id, 'user_id')
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        # Valider les mots de passe
        try:
            validate_password(old_password)
            validate_password(new_password)
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        # Récupérer l'utilisateur
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise CustomError("User not found", 404)

        # Vérifier l'ancien mot de passe
        if not verify_password(user.password, old_password):
            raise CustomError("Invalid current password", 400)

        # Mettre à jour le mot de passe
        updated_user = self.user_repository.update(user_id, password=new_password)

        return updated_user

    def admin_reset_password(self, user_id, new_password):
        """Reset user password by admin
        
        Args:
            user_id (uuid): The ID of the user
            new_password (str): The user's new password
            
        Returns:
            The updated User object
            
        Raises:
            CustomError: if the data is invalid(400), if the user is not found(404)
        """
        try:
            validate_entity_id(user_id, 'user_id')
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        # Récupérer l'utilisateur
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise CustomError("User not found", 404)

        try:
            validate_password(new_password)
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        # Mettre à jour le mot de passe
        updated_user = self.user_repository.update(user_id, password=new_password)
        return updated_user

    def reset_password_by_email(self, email, new_temp_password):
        """Reset password for a user using their email
        
        Args:
            email (str): The user's email
            new_temp_password (str): The generated temporary password
            
        Returns:
            The updated User object
            
        Raises:
            CustomError: if the email is invalid(400), if the user is not found(404)
        """
        try:
            email_validation(email)
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        # Récupérer l'utilisateur par email
        user = self.user_repository.get_by_attribute("email", email)
        if not user:
            raise CustomError("Vous n'avez pas créé de compte", 404)

        try:
            validate_password(new_temp_password)
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        # Mettre à jour le mot de passe
        updated_user = self.user_repository.update(user.id, password=new_temp_password)
        return updated_user
