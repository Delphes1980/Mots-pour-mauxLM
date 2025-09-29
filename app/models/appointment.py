from app.models.baseEntity import (BaseEntity, type_validation, strlen_validation)
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, TYPE_CHECKING
from .user import User
from .prestation import Prestation


class Appointment(BaseEntity):
	__tablename__ = 'appointments'
	_message: Mapped[str] = mapped_column("message", Text, nullable=False)
	_user_id: Mapped[str] = mapped_column("user_id", String(36), ForeignKey('users.id'), nullable=False)
	_prestation_id: Mapped[str] = mapped_column("prestation_id", String(36), ForeignKey('prestations.id'), nullable=False)
	_user: Mapped["User"] = relationship("User", back_populates="appointments", lazy=True)
	_prestation: Mapped["Prestation"] = relationship("Prestation", back_populates="appointments", lazy=True)

	def __init__(self, user: User, message: str, prestation: Prestation):
		super().__init__()
		self.user = user
		self.message = message
		self.prestation = prestation

	@hybrid_property
	def user(self):
		return self._user

	@user.setter
	def user(self, value):
		self._user = self.set_user(value)
		self._user_id = value.id

	@user.expression
	def user(cls):
		return cls._user

	def set_user(self, user):
		""" Valides the user object """
		if user is None:
			raise ValueError("User is required: provide user who writes the appointment")
		type_validation(user, "User", User)
		return user

	@hybrid_property
	def message(self):
		return self._message

	@message.setter
	def message(self, value):
		self._message = self.message_validation(value)

	def message_validation(self, message: str):
		""" Validates the message """
		if message is None:
			raise ValueError('Expected message but received None')
		type_validation(message, 'message', str)
		strlen_validation(message, 'message', 1, 500)
		return message

	@hybrid_property
	def prestation(self):
		return self._prestation
	
	@prestation.setter
	def prestation(self, value):
		self._prestation = self.set_prestation(value)
		self._prestation_id = value.id

	@prestation.expression
	def prestation(cls):
		return cls._prestation

	def set_prestation(self, prestation):
		""" Valides the prestation object """
		if prestation is None:
			raise ValueError("Prestation is required: provide prestation for the appointment")
		type_validation(prestation, "Prestation", Prestation)
		return prestation