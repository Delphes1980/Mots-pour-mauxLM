from uuid import UUID
import inspect
import string
import secrets
import re
from validate_email_address import validate_email
from app import bcrypt
from app import db, create_app


"""
Utility functions for validating input data against class constructors,
Flask-RESTX models, and general data validation.

Functions:
    validate_init_args(some_class, **kwargs):
        Validates that the provided keyword arguments match the
        __init__ signature of the given class. Raises TypeError if
        required arguments are missing or unexpected arguments are
        present.
    compare_data_and_model(data, model):
        Checks that all required fields are present and no unexpected
        fields are included in the input data according to the given
        Flask-RESTX model. Raises ValueError on missing or extra
        fields.
    type_validation(arg, arg_name, *arg_type):
        Validates if an argument is of the expected type(s).
    strlen_validation(string, string_name, min_len, max_len):
        Validates the length of a string within specified range.
    rating_validation(rating):
        Validates review rating value (1-5 range).
    is_valid_uuid4(uuid_str):
        Determines if given string is a valid UUID4.
    name_validation(names, names_name):
        Validates first_name and last_name to ensure they contain only valid characters.
    email_validation(email):
        Validates the email address.
    validate_password(plain_passwrod):
        Validates the password.
    hash_password(validated_password):
        Hash password before storing it
    verify_password(hashed_password, plain_password):
        Verify if the provided password matches the hashed password
    validate_phone_number(phone_number):
        Validates the phone number format
    address_validation(address):
        Validates the address format
    text_field_validation(value, text_field, min_len, max_len):
        Validates the text field format
    admin_validation(is_admin):
        Validates the is_admin field
    validate_entity_id(entity_id, entity_name):
        Validates the entity ID format
    generate_temp_password(length=12, max_attempts=20):
        Generates a temporary password
"""


def validate_init_args(some_class, **kwargs):
    """
    Validate keyword arguments against input parameters of a class.

    Args:
        some_class: The class whose __init__ signature to validate against.
        **kwargs: The keyword arguments to check.

    Raises:
        TypeError: if any required argument is missing or an unexpected
            argument is passed.
    """
    sig = inspect.signature(some_class.__init__)
    params = sig.parameters

    # Remove 'self' from the parameters to validate
    init_params = {name: param for name, param in params.items()
                   if name != 'self'}

    # Check for missing required parameters
    missing = [
        name for name, param in init_params.items()
        if param.default == inspect.Parameter.empty and name not in kwargs
    ]

    # Check for unexpected parameters
    unexpected = [k for k in kwargs if k not in init_params]

    if missing:
        raise TypeError(f"Missing required arguments: {missing}")
    if unexpected:
        raise TypeError(f"Unexpected arguments: {unexpected}")


def compare_data_and_model(data: dict, model):
    """
    Check input provided data against Flask-RESTX model.
    Checks if all required fields defined in a Flask-RESTX model are
    present in the input data, and if it contains unexpected additional
    data.

    Args:
        data (dict): The input data to validate (e.g., request
            payload).
        model: The Flask-RESTX model object (with a __schema__
            attribute).

    Raises:
        ValueError: If any required field is missing from, or any
            unexpected field is present in, the input data.
    """
    # Extract all fields
    all_model_fields = set(model.__schema__.get('properties', {}).keys())
    # Extract all fields marked as 'required'
    required_model_fields = set(model.__schema__.get('required', []))

    # Identify missing required fields
    missing = required_model_fields - set(data)
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Identify extra fields in the input data
    extra = set(data) - all_model_fields
    if extra:
        raise ValueError(f"Unexpected fields: {', '.join(extra)} are "
                         "present")

def rating_validation(rating):
    """
    Validate review rating value.
    
    Args:
        rating: The rating value to validate
        
    Returns:
        int: The validated rating value
        
    Raises:
        ValueError: If rating is invalid (None, wrong type, or out of range)
    """
    if rating is None:
        raise ValueError("Rating is required: provide an integer between 1 and 5")
    type_validation(rating, "rating", int)
    if not (1 <= rating <= 5):
        raise ValueError("Rating must be an integer between 1 and 5, both inclusive")
    return rating

def is_valid_uuid4(uuid_str):
    """Determines if given str is a uuid4"""
    try:
        val = UUID(uuid_str, version=4)
        return val.version == 4
    except ValueError:
        return False

def type_validation(arg, arg_name: str, *arg_type):
    """ Validate if an argument is of the expected type
    Args:
        arg: the argument to validate
        arg_name (str): the name of the argument
        *arg_type: one or more expected types
    Raises:
        TypeError: If the argument's type doesn't match the expected type """

    types_to_check = arg_type[0] if isinstance(arg_type[0], tuple) else arg_type

    if not isinstance(arg, types_to_check):
        if isinstance(types_to_check, tuple):
            type_list = [t.__name__ for t in types_to_check]
            type_string = " or ".join(type_list)
        else:
            type_string = types_to_check.__name__
        raise TypeError(f"Invalid {arg_name}: {arg_name} must be of type {type_string}")
        
def strlen_validation(string: str, string_name: str, min_len, max_len):
    """ Validate the length of a specific range
    Args:
        string (str): the string to validate
        string_name (str): the name of the string
        min_len (int): the minimum length allowed for the string
        max_len (int): the maximum length allowed for the string
    Raises:
    ValueError: If the string's length length is outside the specified min_len and max_len """

    if len(string) < min_len or len(string) > max_len:
        raise ValueError(f"Invalid {string_name}: {string_name} must be shorter than {max_len} characters and include at least {min_len} no-space characters")

def name_validation(names: str, names_name: str):
    """ Validates first_name and last_name to ensure they contain only valid characters """
    if names is None:
        raise ValueError(f'Expected {names_name} but received None')
    type_validation(names, names_name, str)
    names = names.strip()
    strlen_validation(names, names_name, 1, 50)
    names_list = names.split()
    for name in names_list:
        if not re.fullmatch(r"^[^\W\d_]+([.'-][^\W\d_]+)*[.]?$", name, re.UNICODE):
            raise ValueError(f"Invalid {names_name}: {names_name} must contain only letters, apostrophes, spaces, dots or dashes")
    return " ".join(names_list)

def email_validation(email: str):
    """ Validates the email address """
    if email is None:
        raise ValueError('Email attendu mais aucun reçu')
    type_validation(email, 'email', str)
    if not validate_email(email):
        raise ValueError("Adresse e-mail invalide : l'adresse e-mail doit être au format exemple@exemple.com")
    return email

def validate_password(plain_password):
    """ Validates the password to ensure it meets the requirements """
    if plain_password is None:
        raise ValueError("Mot de passe attendu mais aucun reçu")
    if len(plain_password) < 8:
        raise ValueError("Mot de passe invalide : le mot de passe doit comporter au moins 8 caractères")
    if not re.search(r'\d', plain_password):
        raise ValueError("Mot de passe invalide : le mot de passe doit contenir au moins un chiffre")
    if not re.search(r'[A-Z]', plain_password):
        raise ValueError("Mot de passe invalide : le mot de passe doit contenir au moins une lettre majuscule")
    if not re.search(r'[a-z]', plain_password):
        raise ValueError("Mot de passe invalide : le mot de passe doit contenir au moins une lettre minuscule")
    special_chars = r'[!@#$%^&*()_+=\-{}[\]|\\:;"<,>/?`~]'
    if not re.search(special_chars, plain_password):
        raise ValueError("Mot de passe invalide : le mot de passe doit contenir au moins un caractère spécial")
    return plain_password

def hash_password(validated_password):
    """ Hashes the password before storing it """
    if validated_password is None:
        raise ValueError('Expected password but received None')
    type_validation(validated_password, 'password', str)
    return bcrypt.generate_password_hash(validated_password).decode('utf-8')

def verify_password(hashed_password, plain_password):
    """ Verifies if the provided password matches the hashed password """
    if plain_password is None:
        raise ValueError('Expected password but received None')
    return bcrypt.check_password_hash(hashed_password, plain_password)

def validate_phone_number(phone_number: str):
    """Validate the phone number format"""
    if phone_number is None:
        return None
    type_validation(phone_number, 'phone_number', str)
    strlen_validation(phone_number, 'phone_number', 0, 20)
    if not re.fullmatch(r'^\+?[0-9\s\-()]*$', phone_number):
        raise ValueError("Invalid phone number: phone number must contain only digits, spaces, dashes, parentheses and can start with +")
    return phone_number

def address_validation(address: str):
    """Validate the address format"""
    if address is None:
        return None
    type_validation(address, 'address', str)
    strlen_validation(address, 'address', 0, 255)
    return address

def text_field_validation(value, field_name, min_len, max_len):
    """Validate the text field format
    Args:
        value (str): the text to validate
        field_name (str): the name of the text field
        min_len (int): the minimum length allowed for the text
        max_len (int): the maximum length allowed for the text

    Returns:
        str: The validated text field

    Raises:
        ValueError: If the text field's length is outside the specified min_len and max_len
    """
    if value is None:
        raise ValueError(f"Expected {field_name} but received None")
    type_validation(value, field_name, str)
    strlen_validation(value, field_name, min_len, max_len)
    return value

def admin_validation(is_admin):
    """Validates is_admin field"""
    if is_admin is None:
        return False
    type_validation(is_admin, 'is_admin', bool)
    return is_admin

def validate_entity_id(entity_id: str, entity_name: str):
    """Validate the entity ID format
    Args:
        entity_id (str): The ID value
        entity_name (str): The entity name
        
    Returns:
        str: The validated ID
        
    Raises:
        ValueError: if the ID is missing or if the UUID format is invalid
    """
    if not entity_id:
        raise ValueError(f"L'identifiant {entity_name} est requis")
    type_validation(entity_id, entity_name, str)
    if not is_valid_uuid4(entity_id):
        raise ValueError(f"Format d'identifiant {entity_name} invalide")
    return entity_id

def generate_temp_password(length=12, max_attempts=20):
    """Génère un mot de passe temporaire sécurisé et validé après reset du mot de passe par l'admin"""
    alphabet = (string.ascii_letters + string.digits + "!@#$%^&*()_+=-{}[]|\\:;\"<,>/?`~")

    for _ in range(max_attempts):
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(length))
        try:
            if (any(c.isupper() for c in temp_password) and
                any(c.islower() for c in temp_password) and
                any(c.isdigit() for c in temp_password) and
                any(c in "!@#$%^&*()_+=-{}[]|\\:;\"<,>/?`~" for c in temp_password)):
                validate_password(temp_password)
                return temp_password
        except ValueError:
            continue

    raise RuntimeError("Impossible de générer un mot de passe sécurisé après plusieurs tentatives")

class CustomError(Exception):
    """ Custom exception class to handle specific APIs errors with HTTP
    status code"""
    def __init__(self, message, status_code):
        """ Initialize a CustomError instance
        Args:
            message (str): the error message
            satus_code (int): the HTTP status code"""
        super().__init__(message)
        self.status_code = status_code

def db_setup():
    """Crée les tables de la base de données dans le contexte de l'application"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'db_setup':
        db_setup()
