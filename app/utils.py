"""
apiRessources module.

Utility functions for validating input data against class constructors
and Flask-RESTX models.

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
"""
import inspect


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
