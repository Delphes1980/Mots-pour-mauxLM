# app/services/AuthService.py
from app.persistence.UserRepository import UserRepository
from app.utils import (email_validation, validate_password, hash_password, verify_password, validate_entity_id)

class AuthenticationService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    def login(self, email, password):
        """Authenticate user with email/password"""
        email_validation(email)
        validate_password(password)
        
        user = self.user_repository.get_by_attribute("email", email)
        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(user.password, password):
            raise ValueError("Invalid credentials")

        return user

    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        # Valider l'ID de l'utilisateur
        validate_entity_id(user_id, 'user_id')

        # Valider les mots de passe
        validate_password(old_password)

        validate_password(new_password)

        # Récupérer l'utilisateur
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Vérifier l'ancien mot de passe
        if not verify_password(user.password, old_password):
            raise ValueError("Invalid current password")
        
        # Mettre à jour le mot de passe
        updated_user = self.user_repository.update(user_id, password=new_password)

        return updated_user
