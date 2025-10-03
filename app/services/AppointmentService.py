from app.persistence.AppointmentRepository import AppointmentRepository
from app.persistence.UserRepository import UserRepository
from app.persistence.PrestationRepository import PrestationRepository
from app.models.appointment import Appointment
from app.utils import (text_field_validation, validate_entity_id, validate_init_args)
from app.services.mail_service import send_appointment_notifications
from flask import current_app

class AppointmentService:
	def __init__(self):
		self.appointment_repository = AppointmentRepository()
		self.user_repository = UserRepository()
		self.prestation_repository = PrestationRepository()

	def create_appointment(self, **kwargs):
		"""Create a new appointment with the provided data

		Args:
			**kwargs: Appointment data (message, user_id, prestation_id)

		Returns:
			Appointment: Created Appointment

		Raises:
			ValueError: if the data are invalids
		"""		
		# Valider les données
		message = kwargs.get('message')
		text_field_validation(message, 'message', 1, 500)

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

		new_appointment = self.appointment_repository.create_appointment(message, user, prestation)

		practitioner_email = current_app.config.get("MAIL_RECIPIENT_PRACTITIONER")

		if practitioner_email:
			context = {
				'user_full_name' : f"{user.first_name} {user.last_name}",
				'prestation_name' : prestation.name,
				'message' : message
			}

			send_appointment_notifications(
				user_email=user.email,
				practitioner_email=practitioner_email,
				**context
			)

		return new_appointment

	def get_appointment_by_id(self, appointment_id):
		"""Get an appointment by its ID

		Args:
			appointment_id (str): The ID of the appointment to retrieve

		Returns:
			Appointment: The retrieved Appointment

		Raises:
			ValueError: if the ID is invalid or if the appointment does not exist
		"""
		appointment_id = validate_entity_id(appointment_id, 'appointment_id')

		appointment = self.appointment_repository.get_by_id(appointment_id)
		if not appointment:
			raise ValueError("Rendez-vous introuvable")

		return appointment

	def get_all_appointments(self):
		"""Get all appointments

		Returns:
			list: List of all appointments
		"""
		return self.appointment_repository.get_all()

	def get_appointment_by_prestation(self, prestation_id):
		"""Get appointments by prestation ID

		Args:
			prestation_id (str): The ID of the prestation

		Returns:
			list: List of appointments for the given prestation

		Raises:
			ValueError: if the prestation ID is invalid
		"""
		prestation_id = validate_entity_id(prestation_id, 'prestation_id')

		return self.appointment_repository.get_by_prestation_id(prestation_id)

	def get_appointment_by_user(self, user_id):
		"""Get appointment by user ID

		Args:
			user_id (str): The ID of the user

		Returns:
			list: List of appointments for the given user

		Raises:
			ValueError: if the ID is invalid
		"""
		user_id = validate_entity_id(user_id, 'user_id')

		return self.appointment_repository.get_by_user_id(user_id)

	def get_appointment_by_user_and_prestation(self, user_id, prestation_id):
		"""Get appointments by user ID and prestation ID

		Args:
			user_id (str): The ID of the user
			prestation_id (str): The ID of the prestation

		Returns:
			Appointment: The retrieved Appointments

		Raises:
			ValueError: if the IDs are invalid or if the appointments do not exist
		"""
		user_id = validate_entity_id(user_id, 'user_id')

		prestation_id = validate_entity_id(prestation_id, 'prestation_id')

		user = self.user_repository.get_by_id(user_id)
		if not user:
			raise ValueError("Utilisateur non trouvé")

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise ValueError("Prestation non trouvée")

		appointment = self.appointment_repository.get_by_user_and_prestation(user_id, prestation_id)
		if not appointment:
			raise ValueError("Rendez-vous non trouvés pour cet utilisateur et cette prestation")

		return appointment
