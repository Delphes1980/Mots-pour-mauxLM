from app.persistence.UserRepository import UserRepository
from app.utils import (validate_entity_id, admin_validation, name_validation, email_validation, validate_init_args, validate_password, validate_phone_number, address_validation)
from app.models.user import User


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def create_user(self, **kwargs):
        """Create a new user with the provided data
        
        Args:
            **kwargs: User data (first_name, last_name, email, password, address, phone_number, is_admin)
            
        Returns:
            User: Created User
            
        Raises:
            ValueError: if the data are invalids or if the email already exists
        """
        validate_init_args(User, **kwargs)

        # Valider les données
        first_name = kwargs.get('first_name')
        name_validation(first_name, 'first_name')

        last_name = kwargs.get('last_name')
        name_validation(last_name, 'last_name')

        email = kwargs.get('email')
        email_validation(email)

        password = kwargs.get('password')
        validate_password(password)

        address = kwargs.get('address')
        address_validation(address)

        phone_number = kwargs.get('phone_number')
        validate_phone_number(phone_number)

        is_admin_value = kwargs.get('is_admin')
        kwargs['is_admin'] = admin_validation(is_admin_value)

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
        user_id = validate_entity_id(user_id, 'user_id')

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

        if not email:
            raise ValueError("Email is required")

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
        user_id = validate_entity_id(user_id, 'user_id')

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if not kwargs:
            raise ValueError("No data provided for update")

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
            address_validation(address)

        if 'phone_number' in kwargs:
            phone_number = kwargs.get('phone_number')
            validate_phone_number(phone_number)

        if 'password' in kwargs:
            password = kwargs.get('password')
            validate_password(password)

        if 'is_admin' in kwargs:
            is_admin_value = kwargs.get('is_admin')
            kwargs['is_admin'] = admin_validation(is_admin_value)

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
        user_id = validate_entity_id(user_id, 'user_id')

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return self.user_repository.delete(user_id)
