from app.models.baseEntity import (BaseEntity, type_validation, strlen_validation)
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
	from .review import Review
	from .appointment import Appointment


class Prestation(BaseEntity):
	__tablename__ = 'prestations'
	_name: Mapped[str] = mapped_column("name", String(50), nullable=False)
	appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="_prestation", lazy=True)
	reviews: Mapped[List["Review"]] = relationship("Review", back_populates="_prestation", lazy=True)

	def __init__(self, name: str):
		super().__init__()
		self.name = name

	@hybrid_property
	def name(self):
		return self._name

	@name.setter
	def name(self, value: str):
		if value is None:
			raise ValueError('Expected name but received None')
		type_validation(value, 'name', str)
		strlen_validation(value, 'name', 1, 50)
		self._name = value.strip()
