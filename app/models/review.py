from app.models.baseEntity import (BaseEntity, type_validation, strlen_validation)
from app.models.user import User
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.hybrid import hybrid_property


class Review(BaseEntity):
	""" Represents a 'review' entity in the database """
	__tablename__ = 'reviews'
	_text: Mapped[str] = mapped_column("text", Text, nullable=False)
	_rating: Mapped[int] = mapped_column("rating", Integer, nullable=False)
	_user_id: Mapped[str] = mapped_column("user_id", String(36), ForeignKey("users.id"), nullable=False)
	_user: Mapped[User] = relationship("User", back_populates="reviews", lazy=True)
	def __init__(self, text: str, rating: int, user: User):
		super().__init__()
		self.text = text
		self.rating = rating
		self.user = user

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
		self._rating = self.rating_validation(value)

	def rating_validation(self, rating):
		""" Validates the review rating """
		if rating is None:
			raise ValueError("Rating is required: provide an integer between 1 and 5")
		type_validation(rating, "rating", int)
		if not (1 <= rating <= 5):
			raise ValueError("Rating must be an integer between 1 and 5, both inclusive")
		return rating

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
			raise ValueError("User is required: provide user who writes the review")
		type_validation(user, "User", User)
		return user
