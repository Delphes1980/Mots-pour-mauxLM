from app.persistence.AppointmentRepository import AppointmentRepository
from app.persistence.UserRepository import UserRepository
from app.persistence.PrestationRepository import PrestationRepository
from app.models.appointment import Appointment, AppointmentStatus
from app.utils import (text_field_validation, validate_entity_id, CustomError)
from app.services.mail_service import send_appointment_notifications, send_appointment_status_notification
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
			CustomError: if the data are invalids(400), if the appointment is not found(404)
		"""		
		# Valider les données
		message = kwargs.get('message')
		try:
			text_field_validation(message, 'message', 1, 500)
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

		new_appointment = self.appointment_repository.create_appointment(message, user, prestation)

		# Notification Email
		practitioner_email = current_app.config.get("MAIL_RECIPIENT_PRACTITIONER")

		if practitioner_email:
			try:
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
			except Exception as e:
				print(f"Echec de l'envoi de l'email de notification pour le RDV {new_appointment.id}. Erreur: {e}")

		return new_appointment

	def get_appointment_by_id(self, appointment_id):
		"""Get an appointment by its ID

		Args:
			appointment_id (str): The ID of the appointment to retrieve

		Returns:
			Appointment: The retrieved Appointment

		Raises:
			CustomError: if the ID is invalid(400) or if the appointment is not found(404)
		"""
		try:
			appointment_id = validate_entity_id(appointment_id, 'appointment_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		appointment = self.appointment_repository.get_by_id(appointment_id)
		if not appointment:
			raise CustomError("Rendez-vous introuvable", 404)

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
			CustomError: if the prestation ID is invalid(400)
		"""
		try:
			prestation_id = validate_entity_id(prestation_id, 'prestation_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		prestation = self.prestation_repository.get_by_id(prestation_id)
		if not prestation:
			raise CustomError("Prestation non trouvée", 404)
		
		return self.appointment_repository.get_by_prestation_id(prestation_id)

	def get_appointment_by_user(self, user_id):
		"""Get appointments by user ID

		Args:
			user_id (str): The ID of the user

		Returns:
			list: List of appointments for the given user

		Raises:
			CustomError: if the ID is invalid(400)
		"""
		try:
			user_id = validate_entity_id(user_id, 'user_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		user = self.user_repository.get_by_id(user_id)
		if not user:
			raise CustomError("Utilisateur non trouvé", 404)

		return self.appointment_repository.get_by_user_id(user_id)

	def get_appointment_by_user_and_prestation(self, user_id, prestation_id):
		"""Get appointments by user ID and prestation ID

		Args:
			user_id (str): The ID of the user
			prestation_id (str): The ID of the prestation

		Returns:
			Appointment: The retrieved Appointments

		Raises:
			CustomError: if the IDs are invalid(400), if the appointments is not found(404)
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

		appointment = self.appointment_repository.get_by_user_and_prestation(user_id, prestation_id)
		if not appointment:
			raise CustomError("Rendez-vous non trouvés pour cet utilisateur et cette prestation", 404)

		return appointment
	
	def get_appointments_by_status(self, status):
		"""Get appointments by status

		Args:
			status (str): The status of the appointment

		Returns:
			list: List of appointments for the given status

		Raises:
			CustomError: if the status is invalid(400) or if the appointment is not found(404)
		"""
		if not status:
			raise CustomError("Le status du rendez-vous est requis", 400)

		allowed = [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]
		if status not in allowed:
			raise CustomError("Statut de rendez-vous invalide", 400)

		appointments = self.appointment_repository.get_appointments_by_status(status)
		if not appointments:
			raise CustomError("Aucun rendez-vous trouvé", 404)

		return appointments

	def reassign_appointments_from_user(self, old_user_id, new_user_id):
		"""Reassign appointments from an old user to a new user
		
		Args:
			old_user_id (str): The ID of the old user
			new_user_id (str): The ID of the new user
			
			Returns:
				list: List of reassigned appointments
				
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

		appointments = self.appointment_repository.get_by_user_id(old_user_id)
		reassigned_appointments = []

		for appointment in appointments:
			appointment.user = new_user
			reassigned_appointments.append(appointment)

		self.appointment_repository.db.session.commit()

		return reassigned_appointments

	def update_appointment_status(self, appointment_id, **kwargs):
		"""Update the status of an appointment
		
		Args:
			appointment_id (str): The ID of the appointment
			**kwargs: Appointment data (message, user_id, prestation_id, status)

		Returns:
			Appointment: The udpated appointment

		Raises:
			CustomError: If the IDs are invalid(400) or if the appointment is not found(404)
		"""
		try:
			# Vérifier l'ID du RDV
			appointment_id = validate_entity_id(appointment_id, 'appointment_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		# Récupération du RDV
		appointment = self.appointment_repository.get_by_id(appointment_id)
		if not appointment:
			raise CustomError("Rendez-vous non trouvé", 404)
		
		# Vérification de l'utilisateur
		user_id = appointment.user_id
		try:
			try:
				validate_entity_id(user_id, 'user_id')
			except (ValueError, TypeError) as e:
				raise CustomError(str(e), 400)
		
			user = self.user_repository.get_by_id(user_id)
			if not user:
				raise CustomError("Utilisateur lié au rendez-vous introuvable", 404)
		
		except Exception as e:
			raise CustomError(f"Erreur lors de la récupération de l'utilisateur lié au rendez-vous: {e}", 500)

		# Vérification de la prestation
		prestation_id = appointment.prestation_id
		try:
			try:
				validate_entity_id(prestation_id, 'prestation_id')
			except (ValueError, TypeError) as e:
				raise CustomError(str(e), 400)
		
			prestation = self.prestation_repository.get_by_id(prestation_id)
			if not prestation:
				raise CustomError("Prestation introuvable", 404)
			
		except Exception as e:
			raise CustomError(f"Erreur lors de la récupération de la prestation liée au rendez-vous: {e}", 500)

		# Extraction et validation du nouveau status
		new_status = kwargs.get('status')
		if not new_status:
			raise CustomError("Le champ 'status' est requis", 400)

		allowed = [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]

		if new_status not in allowed:
			raise CustomError("Statut de rendez-vous invalide", 400)

		try:
			update_data = {'status': new_status}

			updated_appointment = self.appointment_repository.update(appointment_id, **update_data)

			if new_status in [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED]:
				try:
					message = appointment.message

					context = {
						'user_full_name' : f"{user.first_name} {user.last_name}",
						'prestation_name' : prestation.name,
						'message' : message,
						'status' : new_status
					}

					send_appointment_status_notification(
						user_email=user.email,
						**context
					)

				except Exception as e:
					print(f"Erreur lors de l'envoi de l'email de statut pour le RDV {appointment.id}: {e}")

			return updated_appointment

		except Exception as e:
			raise CustomError(f"Erreur lors de la mise à jour du status du rendez-vous: {e}", 500)

	def delete_appointment(self, appointment_id):
		"""Delete an appointment by its ID

		Args:
			appointment_id (str): The ID of the appointment to delete

		Returns:
			bool: True if the appointment was deleted, False otherwise

		Raises:
			CustomError: if the ID is invalid(400) or if the appointment is not found(404)
		"""
		try:
			appointment_id = validate_entity_id(appointment_id, 'appointment_id')
		except (ValueError, TypeError) as e:
			raise CustomError(str(e), 400)

		appointment = self.appointment_repository.get_by_id(appointment_id)
		if not appointment:
			raise CustomError("Rendez-vous non trouvé", 404)

		return self.appointment_repository.delete(appointment_id)
