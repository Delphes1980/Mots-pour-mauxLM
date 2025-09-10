from app.models.baseEntity import (BaseEntity, type_validation, strlen_validation)
from app.models.user import User
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.hybrid import hybrid_property


class Appointment(BaseEntity):
	__tablename__ = 'appointments'
	_subject: Mapped[str] = mapped_column("subject", String(50), nullable=False)
	_message: Mapped[str] = mapped_column("message", Text(500), nullable=False)
	user_id: Mapped[str] = mapped_column("user_id", String(36), ForeignKey('users.id'), nullable=False)
	_user: Mapped[User] = relationship("User", back_populates="appointments", lazy=True)

	def __init__(self, user: User, subject: str, message: str):
		super().__init__()
		self.user = user
		self.subject = subject
		self.message = message

	@hybrid_property
	def user(self):
		return self._user

	@user.setter
	def user(self, value):
		self._user = self.set_user(value)
		self.user_id = value.id

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
	def subject(self):
		return self._subject

	@subject.setter
	def subject(self, value):
		self._subject = self.subject_validation(value)

	@hybrid_property
	def message(self):
		return self._message

	@message.setter
	def message(self, value):
		self._message = self.message_validation(value)

	def subject_validation(self, subject: str):
		""" Validates the subject """
		if subject is None:
			raise ValueError('Expected subject but received None')
		type_validation(subject, 'subject', str)
		strlen_validation(subject, 'subject', 1, 50)
		return subject

	def message_validation(self, message: str):
		""" Validates the message """
		if message is None:
			raise ValueError('Expected message but received None')
		type_validation(message, 'message', str)
		strlen_validation(message, 'message', 1, 500)
		return message
