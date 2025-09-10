from app.models.baseEntity import (BaseEntity, type_validation, strlen_validation)
from app import bcrypt
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Boolean
import re
from validate_email_address import validate_email
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
	from .review import Review
	from .appointment import Appointment


class User(BaseEntity):
	__tablename__ = 'users'
	_first_name: Mapped[str] = mapped_column("first_name", String(50), nullable=False)
	_last_name: Mapped[str] = mapped_column("last_name", String(50), nullable=False)
	_email: Mapped[str] = mapped_column("email", String(120), nullable=False, unique=True)
	_password: Mapped[str] = mapped_column("password", String(128), nullable=False)
	_is_admin: Mapped[bool] = mapped_column("is_admin", Boolean, default=False)
	reviews: Mapped[List["Review"]] = relationship("Review", back_populates="_user", lazy=True)
	appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="_user", lazy=True)

	def __init__(self, first_name: str, last_name: str, email: str, password: str, is_admin: bool = False):
		super().__init__()
		self.first_name = first_name
		self.last_name = last_name
		self.email = email
		self.is_admin = is_admin
		self.password = password

	@hybrid_property
	def password(self):
		return self._password

	@password.setter
	def password(self, value):
		if value is None:
			raise ValueError('Expected password but received None')
		type_validation(value, 'password', str)
		validated_password = self.validate_password(value)
		self._password = self.hash_password(validated_password)

	def validate_password(self, plain_password):
		""" Validates the password to ensure it meets the requirements """
		if plain_password is None:
			raise ValueError("Expected password but received None")
		if len(plain_password) < 8:
			raise ValueError("Invalid password: password must be at least 8 characters")
		if not re.search(r'\d', plain_password):
			raise ValueError("Invalid password: password must contain at least one digit")
		special_chars = r'[!@#$%^&*()_+=\-{}[\]|\\:;"<,>/?`~]'
		if not re.search(special_chars, plain_password):
			raise ValueError("Invalid password: password must contain at least one special character")
		return plain_password

	def hash_password(self, validated_password):
		""" Hashes the password before storing it """
		if validated_password is None:
			raise ValueError('Expected password but received None')
		type_validation(validated_password, 'password', str)
		return bcrypt.generate_password_hash(validated_password).decode('utf-8')

	def verify_password(self, plain_password):
		""" Verifies if the provided password matches the hashed password """
		if plain_password is None:
			raise ValueError('Expected password but received None')
		return bcrypt.check_password_hash(self.password, plain_password)

	def name_validation(self, names: str, names_name: str):
		""" Validates first_name and last_name to ensure they contain only valid characters """
		if names is None:
			raise ValueError(f'Expected {names_name} but received None')
		type_validation(names, names_name, str)
		names_list = names.strip()
		strlen_validation(names, names_name, 1, 50)
		names_list = names.split()
		for name in names_list:
			if not re.fullmatch(r"^[^\W\d_]+([.'-][^\W\d_]+)*[.]?$", name, re.UNICODE):
				raise ValueError(f"Invalid {names_name}: {names_name} must contain only letters, apostrophes, spaces, dots or dashes")
		return " ".join(names_list)

	def email_validation(self, email: str):
		""" Validates the email address """
		if email is None:
			raise ValueError('Expected email but received None')
		type_validation(email, 'email', str)
		if not validate_email(email):
			raise ValueError("Invalid email: email must have format example@axam.ple")
		return email

	@hybrid_property
	def first_name(self):
		return self._first_name

	@first_name.setter
	def first_name(self, value):
		self._first_name = self.name_validation(value, 'first_name')

	@hybrid_property
	def last_name(self):
		return self._last_name

	@last_name.setter
	def last_name(self, value):
		self._last_name = self.name_validation(value, 'last_name')

	@hybrid_property
	def email(self):
		return self._email

	@email.setter
	def email(self, value: str):
		self._email = self.email_validation(value)

	@hybrid_property
	def is_admin(self):
		return self._is_admin

	@is_admin.setter
	def is_admin(self, value: bool):
		if value is None:
			raise ValueError('Expected is_admin boolean but received None')
		type_validation(value, 'is_admin', bool)
		self._is_admin = value
