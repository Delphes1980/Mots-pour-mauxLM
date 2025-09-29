from app.persistence.UserRepository import UserRepository
from app.utils import (is_valid_uuid4, type_validation, strlen_validation, name_validation, email_validation, validate_init_args)
import re
from app.models.user import User


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def create_user(self, **kwargs):
        """Create a new user with the provided data
        
        Args:
            **kwargs: User data (first_name, last_name, email, password..)
            
        Returns:
            User: Created User
            
        Raises:
            ValueError: if the data are invalids or if the email already exists
        """
        validate_init_args(User, **kwargs)

        email = kwargs.get('email')
        email_validation(email)

        existing_user = self.user_repository.get_by_attribute("email", email)
        if existing_user:
            raise ValueError("Email already exists")
        
        return self.user_repository.create_user(**kwargs)

    def get_user_by_id(self, user_id):
        """Get a user by its ID

        Args:
            user_id (str): The ID of the user to retrieve

        Returns:
            User: The retrieved User

        Raises:
            ValueError: if the ID is invalid or if the user does not exist
        """
        if not is_valid_uuid4(user_id):
            raise ValueError("Invalid user ID")

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return user

    def get_user_by_email(self, email):
        """Get a user by its email

        Args:
            email (str): The email of the user to retrieve

        Returns:
            User: The retrieved User

        Raises:
            ValueError: if the email is invalid or if the user does not exist
        """
        email_validation(email)

        user = self.user_repository.get_by_attribute("email", email)
        if not user:
            raise ValueError("User not found")

        return user

    def get_all_users(self):
        """Get all users

        Returns:
            list: List of all users
        """
        return self.user_repository.get_all()

    def update_user(self, user_id, **kwargs):
        """Update a user by its ID

        Args:
            user_id (str): The ID of the user to update
            **kwargs: User data to update (first_name, last_name, email, password..)

        Returns:
            User: The updated User

        Raises:
            ValueError: if the ID is invalid or if the user does not exist
        """
        if not is_valid_uuid4(user_id):
            raise ValueError("Invalid user ID")

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if 'first_name' in kwargs:
            first_name = kwargs.get('first_name')
            name_validation(first_name, 'first_name')

        if 'last_name' in kwargs:
            last_name = kwargs.get('last_name')
            name_validation(last_name, 'last_name')

        if 'email' in kwargs:
            email = kwargs.get('email')
            email_validation(email)

            existing_user = self.user_repository.get_by_attribute("email", email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already exists")

        if 'address' in kwargs:
            address = kwargs.get('address')
            if address is not None:
                type_validation(address, 'address', str)
                strlen_validation(address, 'address', 0, 255)

        if 'phone_number' in kwargs:
            phone_number = kwargs.get('phone_number')
            if phone_number is not None:
                type_validation(phone_number, 'phone_number', str)
                strlen_validation(phone_number, 'phone_number', 0, 20)
                if not re.fullmatch(r'^\+?[0-9\s\-()]*$', phone_number):
                    raise ValueError("Invalid phone number: phone number must contain only digits, spaces, dashes, parentheses and can start with +")

        return self.user_repository.update(user_id, **kwargs)

    def delete_user(self, user_id):
        """Delete a user by its ID

        Args:
            user_id (str): The ID of the user to delete

        Returns:
            bool: True if the user was deleted, False otherwise

        Raises:
            ValueError: if the ID is invalid or if the user does not exist
        """
        if not is_valid_uuid4(user_id):
            raise ValueError("Invalid user ID")

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return self.user_repository.delete(user_id)
