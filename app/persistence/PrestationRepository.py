from sqlalchemy.exc import SQLAlchemyError
from app.models.prestation import Prestation
from app.persistence.BaseRepository import BaseRepository
from app.utils import (type_validation, strlen_validation)

class PrestationRepository(BaseRepository):
	def __init__(self):
		super().__init__(Prestation)

	def create(self, **kwargs):
		"""Utilise create_prestation() avec validations au lieu de create() dans BaseRepository"""
		return self.create_prestation(kwargs.get('name'))

	def create_prestation(self, name):
		try:
			# Valider le nom de la prestation
			if not name:
				raise ValueError("Le nom de la prestation est requis")
			type_validation(name, 'name', str)
			strlen_validation(name, 'name', 1, 50)

			# Vérifier si la prestation existe déjà
			existing_prestation = self.get_by_attribute("name", name)
			if existing_prestation:
				raise ValueError("La prestation avec ce nom existe déjà")

			# Créer une nouvelle prestation
			new_prestation = Prestation(
				name=name
			)
			self.db.session.add(new_prestation)
			self.db.session.commit()
			return new_prestation
		except SQLAlchemyError:
			raise ValueError("Erreur lors de la création de la prestation")
