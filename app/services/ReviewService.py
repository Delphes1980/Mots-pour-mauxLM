from app.persistence.ReviewRepository import ReviewRepository
from app.persistence.UserRepository import UserRepository
from app.persistence.PrestationRepository import PrestationRepository
from app.models.review import Review
from app.utils import (rating_validation, text_field_validation, validate_entity_id, validate_init_args)


class ReviewService:
	def __init__(self):
		self.review_repository = ReviewRepository()
		self.user_repository = UserRepository()
		self.prestation_repository = PrestationRepository()

	def create_review(self, **kwargs):
		"""Create a new review with the provided data

		Args:
			**kwargs: Review data (rating, text, user_id, prestation_id)

		Returns:
			Review: Created Review

		Raises:
			ValueError: if the data are invalids
		"""

		# Valider les données
		rating = kwargs.get('rating')
		rating_validation(rating)

		text = kwargs.get('text')
		text_field_validation(text, 'text', 2, 500)

		user_id = kwargs.get('user_id')
		validate_entity_id(user_id, 'user_id')

		prestation_id = kwargs.get('prestation_id')
		validate_entity_id(prestation_id, 'prestation_id')

		# Récupérer les objets depuis la base de données
		user = self.user_repository.get_by_id(user_id)
		if not user:
			raise ValueError("Utilisateur introuvable")

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise ValueError("Prestation introuvable")

		# Vérifier si un avis existe déjà
		existing_review = self.review_repository.get_by_user_and_prestation(user_id, prestation_id)
		if existing_review:
			raise ValueError("Un commentaire existe déjà pour cette prestation")

		return self.review_repository.create_review(text, rating, user, prestation)

	def get_review_by_id(self, review_id):
		"""Get a review by its ID
		
		Args:
			review_id (str): The ID of the review to retrieve
			
		Returns:
			Review: The retrieved Review
			
		Raises:
			ValueError: if the ID is invalid or if the review does not exist
		"""
		review_id = validate_entity_id(review_id, 'review_id')
		
		review = self.review_repository.get_by_id(review_id)
		if not review:
			raise ValueError("Commentaire non trouvé")

		return review

	def get_all_reviews(self):
		"""Get all reviews

		Returns:
			list: List of all reviews
		"""
		return self.review_repository.get_all()

	def get_review_by_prestation(self, prestation_id):
		"""Get reviews by prestation ID

		Args:
			prestation_id (str): The ID of the prestation

		Returns:
			list: List of reviews for the given prestation

		Raises:
			ValueError: if the ID is invalid
		"""
		prestation_id = validate_entity_id(prestation_id, 'prestation_id')

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise ValueError("Prestation non trouvée")

		return self.review_repository.get_by_prestation_id(prestation_id)

	def get_review_by_user(self, user_id):
		"""Get reviews by user ID

		Args:
			user_id (str): The ID of the user

		Returns:
			list: List of reviews for the given user

		Raises:
			ValueError: if the ID is invalid
		"""
		user_id = validate_entity_id(user_id, 'user_id')

		user = self.user_repository.get_by_id(user_id)
		if not user:
			raise ValueError("Utilisateur non trouvé")

		return self.review_repository.get_by_user_id(user_id)
	
	def get_review_by_user_and_prestation(self, user_id, prestation_id):
		"""Get reviews by user ID and prestation ID

		Args:
			user_id (str): The ID of the user
			prestation_id (str): The ID of the prestation

		Returns:
			Review: The retrieved Reviews

		Raises:
			ValueError: if the IDs are invalid or if the reviews do not exist
		"""
		user_id = validate_entity_id(user_id, 'user_id')

		prestation_id = validate_entity_id(prestation_id, 'prestation_id')

		user = self.user_repository.get_by_id(user_id)
		if not user:
			raise ValueError("Utilisateur non trouvé")

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise ValueError("Prestation non trouvée")

		review = self.review_repository.get_by_user_and_prestation(user_id, prestation_id)
		if not review:
			raise ValueError("Commentaires non trouvés pour cet utilisateur et cette prestation")

		return review

	def update_review(self, review_id, **kwargs):
		"""Update a review by its ID

		Args:
			review_id (str): The ID of the review to update
			**kwargs: Review data to update (rating, text)

		Returns:
			Review: The updated Review

		Raises:
			ValueError: if the ID is invalid or if the review does not exist
		"""
		review_id = validate_entity_id(review_id, 'review_id')

		existing_review = self.review_repository.get_by_id(review_id)
		if not existing_review:
			raise ValueError("Commentaire non trouvé")

		if not kwargs:
			raise ValueError("Aucune donnée fournie pour la mise à jour")

		if 'rating' in kwargs:
			rating = kwargs.get('rating')
			rating_validation(rating)

		if 'text' in kwargs:
			text = kwargs.get('text')
			text_field_validation(text, 'text', 2, 500)

		return self.review_repository.update(review_id, **kwargs)

	def delete_review(self, review_id):
		"""Delete a review by its ID

		Args:
			review_id (str): The ID of the review to delete

		Returns:
			bool: True if the review was deleted, False otherwise

		Raises:
			ValueError: If the ID is invalid or if the review does not exist
		"""
		review_id = validate_entity_id(review_id, 'review_id')

		review = self.review_repository.get_by_id(review_id)
		if not review:
			raise ValueError("Commentaire non trouvé")

		return self.review_repository.delete(review_id)
