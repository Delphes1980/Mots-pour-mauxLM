import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app import db

class BaseEntity(db.Model):
	__abstract__ = True
	id: Mapped[str] = mapped_column(String(36), default=lambda: str(uuid.uuid4()), primary_key=True, nullable=False, unique=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc))
	updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

	def __init__(self):
		self.id = str(uuid.uuid4())
		self.created_at = datetime.now(timezone.utc)
		self.updated_at = datetime.now(timezone.utc)

	def save(self):
		""" Update the updated_at timestamp whenever the object is modified """
		self.updated_at = datetime.now(timezone.utc)

	def update(self, data):
		""" Update the attributes of the object based on the provided dictionary """
		for key, value in data.items():
			if hasattr(self, key):
				setattr(self, key, value)
		self.save()  # Update the updated_at timestamp
