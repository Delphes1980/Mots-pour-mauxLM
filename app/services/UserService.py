from app.persistence.UserRepository import UserRepository
from app.persistence.ReviewRepository import ReviewRepository
from app.persistence.AppointmentRepository import AppointmentRepository
from app.utils import (validate_entity_id, admin_validation, name_validation, email_validation, validate_init_args, validate_password, validate_phone_number, address_validation, CustomError)
from app.models.user import User


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.review_repository = ReviewRepository()
        self.appointment_repository = AppointmentRepository()

    def create_user(self, **kwargs):
        """Create a new user with the provided data
        
        Args:
            **kwargs: User data (first_name, last_name, email, password, address, phone_number, is_admin)
            
        Returns:
            User: Created User
            
        Raises:
            CustomError: if the data are invalids(400) or if the email already exists(409)
        """
        validate_init_args(User, **kwargs)

        # Valider les données
        first_name = kwargs.get('first_name')
        try:
            name_validation(first_name, 'first_name')
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        last_name = kwargs.get('last_name')
        try:
            name_validation(last_name, 'last_name')
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        email = kwargs.get('email')
        try:
            email_validation(email)
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        password = kwargs.get('password')
        try:
            validate_password(password)
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        address = kwargs.get('address')
        try:
            address_validation(address)
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        phone_number = kwargs.get('phone_number')
        try:
            validate_phone_number(phone_number)
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        is_admin_value = kwargs.get('is_admin')
        try:
            kwargs['is_admin'] = admin_validation(is_admin_value)
        except TypeError as e:
            raise CustomError(str(e), 400) from e

        existing_user = self.user_repository.get_by_attribute("email", email)
        if existing_user:
            raise CustomError("Email already exists", 409)

        return self.user_repository.create_user(**kwargs)

    def admin_create_user(self, temp_password, **kwargs):
        """Create a new user with the provided data by admin
        
        Args:
            temp_password (str): Temporary password for the user
            **kwargs: User data (first_name, last_name, email, address, phone_number, is_admin)
            
        Returns:
            User: Created User

        Raises:
            CustomError: if the data are invalids(400) or if the email already exists(409)
        """
        kwargs['password'] = temp_password

        validate_init_args(User, **kwargs)

        # Valider les données
        first_name = kwargs.get('first_name')
        try:
            name_validation(first_name, 'first_name')
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        last_name = kwargs.get('last_name')
        try:
            name_validation(last_name, 'last_name')
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        email = kwargs.get('email')
        try:
            email_validation(email)
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        address = kwargs.get('address')
        try:
            address_validation(address)
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        phone_number = kwargs.get('phone_number')
        try:
            validate_phone_number(phone_number)
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        is_admin_value = kwargs.get('is_admin')
        try:
            kwargs['is_admin'] = admin_validation(is_admin_value)
        except TypeError as e:
            raise CustomError(str(e), 400) from e

        existing_user = self.user_repository.get_by_attribute("email", email)
        if existing_user:
            raise CustomError("Email already exists", 409)

        return self.user_repository.admin_create_user(**kwargs)

    def get_user_by_id(self, user_id):
        """Get a user by its ID

        Args:
            user_id (str): The ID of the user to retrieve

        Returns:
            User: The retrieved User

        Raises:
            CustomError: if the ID is invalid(400) or if the user is not found(404)
        """
        try:
            user_id = validate_entity_id(user_id, 'user_id')
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise CustomError("User not found", 404)

        return user

    def get_user_by_email(self, email):
        """Get a user by its email

        Args:
            email (str): The email of the user to retrieve

        Returns:
            User: The retrieved User

        Raises:
            CustomError: if the email is invalid(400) or if the user is not found(404)
        """
        try:
            email_validation(email)
        except ValueError as e:
            raise CustomError(str(e), 400) from e

        if not email:
            raise CustomError("Email is required", 400)

        user = self.user_repository.get_by_attribute("email", email)
        if not user:
            raise CustomError("User not found", 404)

        return user

    def search_users_by_email_fragment(self, fragment):
        """Search users by email fragment

        Args:
            fragment (str): The email fragment to search for

        Returns:
            list: List of users matching the email fragment

        Raises:
            CustomError: if the fragment is invalid(400)
        """
        if not fragment or not isinstance(fragment, str):
            raise CustomError("Invalid email fragment", 400)

        users = self.user_repository.search_by_email_fragment(fragment)
        if not users:
            raise CustomError('No user found', 404)

        return users

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
            CustomError: if the ID is invalid(400), if the user is not found(404), if the user already exists(409)
        """
        try:
            user_id = validate_entity_id(user_id, 'user_id')
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise CustomError("User not found", 404)

        if not kwargs:
            raise CustomError("No data provided for update", 400)

        if 'first_name' in kwargs:
            first_name = kwargs.get('first_name')
            try:
                name_validation(first_name, 'first_name')
            except ValueError as e:
                raise CustomError(str(e), 400) from e

        if 'last_name' in kwargs:
            last_name = kwargs.get('last_name')
            try:
                name_validation(last_name, 'last_name')
            except ValueError as e:
                raise CustomError(str(e), 400) from e

        if 'email' in kwargs:
            email = kwargs.get('email')
            try:
                email_validation(email)
            except ValueError as e:
                raise CustomError(str(e), 400) from e

            existing_user = self.user_repository.get_by_attribute("email", email)
            if existing_user and existing_user.id != user_id:
                raise CustomError("Email already exists", 409)

        if 'address' in kwargs:
            address = kwargs.get('address')
            if address and address.strip() != "":
                try:
                    address_validation(address)
                except (ValueError, TypeError) as e:
                    raise CustomError(str(e), 400) from e
            else:
                kwargs['address'] = None

        if 'phone_number' in kwargs:
            phone_number = kwargs.get('phone_number')
            if phone_number and phone_number.strip() != "":
                try:
                    validate_phone_number(phone_number)
                except (ValueError, TypeError) as e:
                    raise CustomError(str(e), 400) from e
            else:
                kwargs['phone_number'] = None

        if 'password' in kwargs:
            password = kwargs.get('password')
            try:
                validate_password(password)
            except ValueError as e:
                raise CustomError(str(e), 400) from e

        if 'is_admin' in kwargs:
            is_admin_value = kwargs.get('is_admin')
            try:
                kwargs['is_admin'] = admin_validation(is_admin_value)
            except TypeError as e:
                raise CustomError(str(e), 400) from e

        return self.user_repository.update(user_id, **kwargs)

    def delete_user(self, user_id):
        """Delete a user by its ID

        Args:
            user_id (str): The ID of the user to delete

        Returns:
            bool: True if the user was deleted, False otherwise

        Raises:
            CustomError: if the ID is invalid(400) or if the user is not found(404)
        """
        # Valider les identifiants
        try:
            user_id = validate_entity_id(user_id, 'user_id')
        except (ValueError, TypeError) as e:
            raise CustomError(str(e), 400) from e

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise CustomError("User not found", 404)

        if user.email == 'deleted@system.local':
            raise CustomError('You can not delete ghost user', 403)

        ghost_user = self.user_repository.get_by_attribute('email', 'deleted@system.local')
        if not ghost_user:
            raise CustomError("Ghost user not found", 404)

        # Vérifier si des avis existent pour cet utilisateur
        reviews = self.review_repository.get_by_user_id(user_id)
        if reviews:
            self.review_repository.reassign_reviews_from_user(user.id, ghost_user.id)

        # Vérifier si des rendez-vous existent pour cet utilisateur
        appointments = self.appointment_repository.get_by_user_id(user_id)
        if appointments:
            self.appointment_repository.reassign_appointments_from_user(user.id, ghost_user.id)

        return self.user_repository.delete(user_id)
