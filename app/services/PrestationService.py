from app.persistence.PrestationRepository import PrestationRepository
from app.models.prestation import Prestation
from app.utils import (validate_init_args, name_validation, validate_entity_id)


class PrestationService:
	def __init__(self):
		self.prestation_repository = PrestationRepository()

	def create_prestation(self, **kwargs):
		"""Create a new prestation with the provided data

		Args:
			**kwargs: Prestation data (name)

		Returns:
			Prestation: Created Prestation

		Raises:
			ValueError: if the data are invalids
		"""
		# Valider que tous les champs requis sont présents
		validate_init_args(Prestation, **kwargs)

		# Valider les données
		name = kwargs.get('name')
		name_validation(name, 'name')
		existing_prestation = self.prestation_repository.get_by_attribute("name", name)
		if existing_prestation:
			raise ValueError("La prestation existe déjà")

		return self.prestation_repository.create_prestation(**kwargs)

	def get_prestation_by_id(self, prestation_id):
		"""Get a prestation by its ID

		Args:
			prestation_id (str): The ID of the prestation to retrieve

		Returns:
			Prestation: The retrieved Prestation

		Raises:
			ValueError: if the ID is invalid or if the prestation does not exist
		"""
		prestation_id = validate_entity_id(prestation_id, 'prestation_id')

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise ValueError("Prestation non trouvée")

		return prestation

	def get_all_prestations(self):
		"""Get all prestations

		Returns:
			list: List of all prestations
		"""
		return self.prestation_repository.get_all()

	def get_prestation_by_name(self, name):
		"""Get a prestation by its name

		Args:
			name (str): The name of the prestation to retrive

		Returns:
			Prestation: The retrieved Prestation

		Raises:
			ValueError: if the name is invalid or if the prestation does not exist
		"""
		if not name:
			raise ValueError("Le nom de la prestation est requis")

		name_validation(name, 'name')

		prestation = self.prestation_repository.get_by_attribute("name", name)
		if not prestation:
			raise ValueError("Prestation non trouvée")

		return prestation

	def update_prestation(self, prestation_id, **kwargs):
		"""Update a prestation by its ID
		
		Args:
			name_id (str): The ID of the prestation to update
			**kwargs: Prestation data to update (name)

		Returns:
			Prestation: The updated Prestation

		Raises:
			ValueError: if the ID is invalid or if the prestation does not exist
		"""
		prestation_id = validate_entity_id(prestation_id, 'prestation_id')

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise ValueError("Prestation non trouvée")

		if not kwargs:
			raise ValueError("Aucune donnée à mettre à jour")

		if 'name' in kwargs:
			name = kwargs.get('name')
			name_validation(name, 'name')
			existing_prestation = self.prestation_repository.get_by_attribute("name", name)
			if existing_prestation and existing_prestation.id != prestation_id:
				raise ValueError("Prestation déjà existante")

		return self.prestation_repository.update(prestation_id, **kwargs)

	def delete_prestation(self, prestation_id):
		"""Delete a prestation by its ID

		Args:
			prestation_id (str): The ID of the prestation to delete

		Returns:
			bool: True if the prestation was deleted, False otherwise

		Raises:
			ValueError: if the ID is invalid or if the prestation does not exist
		"""
		prestation_id = validate_entity_id(prestation_id, 'prestation_id')

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise ValueError("Prestation non trouvée")

		return self.prestation_repository.delete(prestation_id)
