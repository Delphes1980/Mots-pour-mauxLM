from app.models.baseEntity import BaseEntity
from app.utils import (rating_validation, type_validation, strlen_validation)
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, TYPE_CHECKING
from .user import User
from .prestation import Prestation


class Review(BaseEntity):
	""" Represents a 'review' entity in the database """
	__tablename__ = 'reviews'
	_text: Mapped[str] = mapped_column("text", Text, nullable=False)
	_rating: Mapped[int] = mapped_column("rating", Integer, nullable=False)
	_user_id: Mapped[str] = mapped_column("user_id", String(36), ForeignKey("users.id"), nullable=False)
	_prestation_id: Mapped[str] = mapped_column("prestation_id", String(36), ForeignKey("prestations.id"), nullable=False)
	_user: Mapped["User"] = relationship("User", back_populates="reviews", lazy=True)
	_prestation: Mapped["Prestation"] = relationship("Prestation", back_populates="reviews", lazy=True)

	def __init__(self, text: str, rating: int, user: User, prestation: Prestation):
		super().__init__()
		self.text = text
		self.rating = rating
		self.user = user
		self.prestation = prestation

	@hybrid_property
	def text(self):
		return self._text

	@text.setter
	def text(self, value):
		if value is None:
			raise ValueError("Text is required: provide content for the review")
		type_validation(value, "text", str)
		value = value.strip()
		strlen_validation(value, "text", 2, 500)
		self._text = value

	@hybrid_property
	def rating(self):
		return self._rating

	@rating.setter
	def rating(self, value):
		self._rating = rating_validation(value)

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
		""" Validates the user object """
		if user is None:
			raise ValueError("User is required: provide user who writes the review")
		type_validation(user, "User", User)
		return user

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
		""" Validates the prestation object """
		if prestation is None:
			raise ValueError("Prestation is required: provide prestation being reviewed")
		type_validation(prestation, "Prestation", Prestation)
		return prestation
