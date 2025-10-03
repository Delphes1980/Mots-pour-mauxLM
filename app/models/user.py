from app.models.baseEntity import BaseEntity
from app.utils import (type_validation, strlen_validation, name_validation, email_validation, validate_password, hash_password)
from app import bcrypt
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Boolean
import re
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
	from .review import Review
	from .appointment import Appointment


class User(BaseEntity):
	__tablename__ = 'users'
	_first_name: Mapped[str] = mapped_column("first_name", String(50), nullable=False)
	_last_name: Mapped[str] = mapped_column("last_name", String(50), nullable=False)
	_email: Mapped[str] = mapped_column("email", String(120), nullable=False, unique=True)
	_password: Mapped[str] = mapped_column("password", String(128), nullable=False)
	_address: Mapped[Optional[str]] = mapped_column("address", String(255), nullable=True)
	_phone_number: Mapped[Optional[str]] = mapped_column("phone_number", String(20), nullable=True)
	_is_admin: Mapped[bool] = mapped_column("is_admin", Boolean, default=False)
	reviews: Mapped[List["Review"]] = relationship("Review", back_populates="_user", lazy=True)
	appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="_user", lazy=True)

	def __init__(self, first_name: str, last_name: str, email: str,password: str, address: Optional[str] = None, phone_number: Optional[str] = None, is_admin: bool = False):
		super().__init__()
		self.first_name = first_name
		self.last_name = last_name
		self.email = email
		self.address = address
		self.phone_number = phone_number
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
		validated_password = validate_password(value)
		self._password = hash_password(validated_password)

	@hybrid_property
	def first_name(self):
		return self._first_name

	@first_name.setter
	def first_name(self, value):
		self._first_name = name_validation(value, 'first_name')

	@hybrid_property
	def last_name(self):
		return self._last_name

	@last_name.setter
	def last_name(self, value):
		self._last_name = name_validation(value, 'last_name')

	@hybrid_property
	def email(self):
		return self._email

	@email.setter
	def email(self, value: str):
		self._email = email_validation(value)

	@hybrid_property
	def is_admin(self):
		return self._is_admin

	@is_admin.setter
	def is_admin(self, value: bool):
		if value is None:
			raise ValueError('Expected is_admin boolean but received None')
		type_validation(value, 'is_admin', bool)
		self._is_admin = value

	@hybrid_property
	def address(self):
		return self._address
	
	@address.setter
	def address(self, value: Optional[str]):
		if value is None:
			self._address = None
		else:
			type_validation(value, 'address', str)
			strlen_validation(value, 'address', 0, 255)
			self._address = value

	@hybrid_property
	def phone_number(self):
		return self._phone_number
	
	@phone_number.setter
	def phone_number(self, value: Optional[str]):
		if value is None:
			self._phone_number = None
		else:
			type_validation(value, 'phone_number', str)
			strlen_validation(value, 'phone_number', 0, 20)
			if not re.fullmatch(r'^\+?[0-9\s\-()]*$', value):
				raise ValueError("Invalid phone number: phone number must contain only digits, spaces, dashes, parentheses and can start with +")
			self._phone_number = value
