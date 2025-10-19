from app.persistence.ReviewRepository import ReviewRepository
from app.persistence.UserRepository import UserRepository
from app.persistence.PrestationRepository import PrestationRepository
from app.models.review import Review
from app.utils import (rating_validation, text_field_validation, validate_entity_id, CustomError)


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
			CustomError: if the data are invalids(400), if review is not found(404), if the review already exists(409)
		"""

		# Valider les données
		rating = kwargs.get('rating')
		try:
			rating_validation(rating)
		except ValueError as e:
			raise CustomError(str(e), 400)

		text = kwargs.get('text')
		try:
			text_field_validation(text, 'text', 2, 500)
		except ValueError as e:
			raise CustomError(str(e), 400)

		user_id = kwargs.get('user_id')
		try:
			validate_entity_id(user_id, 'user_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		prestation_id = kwargs.get('prestation_id')
		try:
			validate_entity_id(prestation_id, 'prestation_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		# Récupérer les objets depuis la base de données
		user = self.user_repository.get_by_id(user_id)
		if not user:
			raise CustomError("Utilisateur introuvable", 404)

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise CustomError("Prestation introuvable", 404)

		# Vérifier si un avis existe déjà
		existing_review = self.review_repository.get_by_user_and_prestation(user_id, prestation_id)
		if existing_review:
			raise CustomError("Un commentaire existe déjà pour cette prestation", 409)

		return self.review_repository.create_review(text, rating, user, prestation)

	def get_review_by_id(self, review_id):
		"""Get a review by its ID
		
		Args:
			review_id (str): The ID of the review to retrieve
			
		Returns:
			Review: The retrieved Review
			
		Raises:
			CustomError: if the ID is invalid(400) or if the review is not found(404)
		"""
		try:
			review_id = validate_entity_id(review_id, 'review_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)
		
		review = self.review_repository.get_by_id(review_id)
		if not review:
			raise CustomError("Commentaire non trouvé", 404)

		return review

	def get_all_reviews(self):
		"""Get all reviews

		Returns:
			list: List of all reviews
		"""
		return self.review_repository.get_all()

	def get_all_public_reviews(self):
		"""Get all public reviews

		Returns:
		list: List of all reviews
		"""
		try:
			reviews = self.review_repository.get_all_public_reviews()
			public_reviews = []

			for review in reviews:
				user = review.user

				# Déterminer le nom de l'auteur
				if not user:
					user_first_name = 'Utilisateur anonyme'
					user_last_name = ''
				else:
					first_name_clean = user.first_name.strip().lower()
					last_name_clean = user.last_name.strip().lower()

					if first_name_clean == 'ghost' and last_name_clean == 'user':
						user_first_name = 'Utilisateur anonyme'
						user_last_name = ''
					else:
						# Capitalisation des prénoms composé
						segments = user.first_name.strip().split('-')
						capitalized_segments = [segment.capitalize() for segment in segments]
						user_first_name = '-'.join(capitalized_segments)

						if user.last_name:
							user_last_name = user.last_name.strip()[0].upper() + '.'
						else:
							user_last_name = ''

					public_reviews.append({
						'id': str(review.id),
						'rating': review.rating,
						'text': review.text,
						'user': {
							'id': str(user.id) if user else None,
							'first_name': user_first_name,
							'last_name': user_last_name
						}
					})

			return public_reviews
			
		except Exception as e:
			raise CustomError('Erreur lors de la récupération des commentaires publics', 500)

	def get_review_by_prestation(self, prestation_id):
		"""Get reviews by prestation ID

		Args:
			prestation_id (str): The ID of the prestation

		Returns:
			list: List of reviews for the given prestation

		Raises:
			CustomError: if the ID is invalid(400) and if the prestation is not found(404)
		"""
		try:
			prestation_id = validate_entity_id(prestation_id, 'prestation_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise CustomError("Prestation non trouvée", 404)

		return self.review_repository.get_by_prestation_id(prestation_id)

	def get_review_by_user(self, user_id):
		"""Get reviews by user ID

		Args:
			user_id (str): The ID of the user

		Returns:
			list: List of reviews for the given user

		Raises:
			CustomError: if the ID is invalid(400) and if the user is not found(404)
		"""
		try:
			user_id = validate_entity_id(user_id, 'user_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		user = self.user_repository.get_by_id(user_id)
		if not user:
			raise CustomError("Utilisateur non trouvé", 404)

		return self.review_repository.get_by_user_id(user_id)
	
	def get_review_by_user_and_prestation(self, user_id, prestation_id):
		"""Get reviews by user ID and prestation ID

		Args:
			user_id (str): The ID of the user
			prestation_id (str): The ID of the prestation

		Returns:
			Review: The retrieved Reviews

		Raises:
			CustomError: if the IDs are invalid(400) or if the reviews are not found(404)
		"""
		try:
			user_id = validate_entity_id(user_id, 'user_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		try:
			prestation_id = validate_entity_id(prestation_id, 'prestation_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		user = self.user_repository.get_by_id(user_id)
		if not user:
			raise CustomError("Utilisateur non trouvé", 404)

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise CustomError("Prestation non trouvée", 404)

		review = self.review_repository.get_by_user_and_prestation(user_id, prestation_id)
		if not review:
			raise CustomError("Commentaires non trouvés pour cet utilisateur et cette prestation", 404)

		return review

	def update_review(self, review_id, current_user_id, **kwargs):
		"""Update a review by its ID

		Args:
			review_id (str): The ID of the review to update
			current_user_id (str): The ID of the current user
			**kwargs: Review data to update (rating, text)

		Returns:
			Review: The updated Review

		Raises:
			CustomError: if the ID is invalid(400) or if the review is not found(404)
		"""
		try:
			review_id = validate_entity_id(review_id, 'review_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		try:
			current_user_id = validate_entity_id(current_user_id, 'current_user_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		existing_review = self.review_repository.get_by_id(review_id)
		if not existing_review:
			raise CustomError("Commentaire non trouvé", 404)

		existing_prestation = self.prestation_repository.get_by_id(existing_review.prestation_id)
		if not existing_prestation:
			raise CustomError('La prestation associée au commentaire n\'a pas été trouvée', 404)

		current_user = self.user_repository.get_by_id(current_user_id)
		if not current_user:
			raise CustomError('L\'utilisateur n\a pas été trouvé', 404)
		
		if current_user.is_admin:
			raise CustomError('L\'administrateur ne peut pas modifier un commentaire', 403)
		
		if str(existing_review.user_id) != str(current_user_id):
			raise CustomError('Vous ne pouvez pas modifier le commentaire de quelqu\'un d\'autre', 403)

		if not kwargs:
			raise CustomError("Aucune donnée fournie pour la mise à jour", 400)

		if 'rating' in kwargs:
			rating = kwargs.get('rating')
			try:
				rating_validation(rating)
			except ValueError as e:
				raise CustomError(str(e), 400)

		if 'text' in kwargs:
			text = kwargs.get('text')
			try:
				text_field_validation(text, 'text', 2, 500)
			except ValueError as e:
				raise CustomError(str(e), 400)

		return self.review_repository.update(review_id, **kwargs)

	def delete_review(self, review_id):
		"""Delete a review by its ID

		Args:
			review_id (str): The ID of the review to delete

		Returns:
			bool: True if the review was deleted, False otherwise

		Raises:
			CustomError: If the ID is invalid(400) or if the review is not found(404)
		"""
		try:
			review_id = validate_entity_id(review_id, 'review_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		review = self.review_repository.get_by_id(review_id)
		if not review:
			raise CustomError("Commentaire non trouvé", 404)

		return self.review_repository.delete(review_id)

	def reassign_reviews_from_user(self, old_user_id, new_user_id):
		"""Reassign reviews from an old user to a new user

		Args:
			old_user_id (str): The ID of the old user
			new_user_id (str): The ID of the new user

		Returns:
			list: List of reassigned reviews

		Raises:
			CustomError: If the IDs are invalid(400) or if the users are not found(404)
		"""
		try:
			old_user_id = validate_entity_id(old_user_id, 'old_user_id')
			new_user_id = validate_entity_id(new_user_id, 'new_user_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		old_user = self.user_repository.get_by_id(old_user_id)
		if not old_user:
			raise CustomError("Ancien utilisateur non trouvé", 404)

		new_user = self.user_repository.get_by_id(new_user_id)
		if not new_user:
			raise CustomError("Nouvel utilisateur non trouvé", 404)

		reviews = self.review_repository.get_by_user_id(old_user_id)
		reassigned_reviews = []

		for review in reviews:
			review.user = new_user
			reassigned_reviews.append(review)

		self.review_repository.db.session.commit()

		return reassigned_reviews

	def reassign_reviews_from_prestation(self, old_prestation_id, new_prestation_id):
		"""Reassign reviews from an old prestation to a new prestation

		Args:
			old_prestation_id (str): The ID of the old prestation
			new_prestation_id (str): The ID of the new prestation

		Returns:
			list: List of reassigned reviews

		Raises:
			CustomError: If the IDs are invalid(400) or if the prestations are not found(404)
		"""
		try:
			old_prestation_id = validate_entity_id(old_prestation_id, 'old_prestation_id')
			new_prestation_id = validate_entity_id(new_prestation_id, 'new_prestation_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		old_prestation = self.prestation_repository.get_by_id(old_prestation_id)
		if not old_prestation:
			raise CustomError("Ancienne prestation non trouvée", 404)

		new_prestation = self.prestation_repository.get_by_id(new_prestation_id)
		if not new_prestation:
			raise CustomError("Nouvelle prestation non trouvée", 404)

		reviews = self.review_repository.get_by_prestation_id(old_prestation_id)
		reassigned_reviews = []

		for review in reviews:
			review.prestation = new_prestation
			reassigned_reviews.append(review)

		self.review_repository.db.session.commit()

		return reassigned_reviews