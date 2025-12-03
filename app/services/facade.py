from app.services.UserService import UserService
from app.services.ReviewService import ReviewService
from app.services.AppointmentService import AppointmentService
from app.services.PrestationService import PrestationService
from app.services.AuthenticationService import AuthenticationService


class Facade:
    def __init__(self):
        self.user_service = UserService()
        self.review_service = ReviewService()
        self.appointment_service = AppointmentService()
        self.prestation_service = PrestationService()
        self.authentication_service = AuthenticationService()

    # User CRUD operations
    def create_user(self, **kwargs):
        return self.user_service.create_user(**kwargs)

    def admin_create_user(self, temp_password, **kwargs):
        return self.user_service.admin_create_user(temp_password, **kwargs)

    def get_user_by_id(self, user_id):
        return self.user_service.get_user_by_id(user_id)

    def get_user_by_email(self, email):
        return self.user_service.get_user_by_email(email)
    
    def search_users_by_email_fragment(self, fragment):
        return self.user_service.search_users_by_email_fragment(fragment)

    def get_all_users(self):
        return self.user_service.get_all_users()

    def update_user(self, user_id, **kwargs):
        return self.user_service.update_user(user_id, **kwargs)

    def delete_user(self, user_id):
        return self.user_service.delete_user(user_id)

    # Authentification
    def login(self, email, password):
        return self.authentication_service.login(email, password)

    def change_password(self, user_id, old_password, new_password):
        return self.authentication_service.change_password(user_id, old_password, new_password)

    def admin_reset_password(self, user_id, new_password):
        return self.authentication_service.admin_reset_password(user_id, new_password)

    def reset_password_by_email(self, email, temp_password):
        return self.authentication_service.reset_password_by_email(email, temp_password)

    # Review CRUD operations
    def create_review(self, **kwargs):
        return self.review_service.create_review(**kwargs)

    def get_review_by_id(self, review_id):
        return self.review_service.get_review_by_id(review_id)

    def get_all_reviews(self):
        return self.review_service.get_all_reviews()

    def get_all_public_reviews(self):
        return self.review_service.get_all_public_reviews()

    def get_review_by_prestation(self, prestation_id):
        return self.review_service.get_review_by_prestation(prestation_id)

    def get_review_by_user(self, user_id):
        return self.review_service.get_review_by_user(user_id)

    def get_review_by_user_and_prestation(self, user_id, prestation_id):
        return self.review_service.get_review_by_user_and_prestation(user_id, prestation_id)

    def update_review(self, review_id, **kwargs):
        return self.review_service.update_review(review_id, **kwargs)

    def delete_review(self, review_id):
        return self.review_service.delete_review(review_id)

    def reassign_reviews_from_user(self, old_user_id, new_user_id):
        return self.review_service.reassign_reviews_from_user(old_user_id, new_user_id)

    def reassign_reviews_from_prestation(self, old_prestation_id, new_prestation_id):
        return self.review_service.reassign_reviews_from_prestation(old_prestation_id, new_prestation_id)

    # Appointment CRUD operations
    def create_appointment(self, **kwargs):
        return self.appointment_service.create_appointment(**kwargs)

    def get_appointment_by_id(self, appointment_id):
        return self.appointment_service.get_appointment_by_id(appointment_id)

    def get_all_appointments(self):
        return self.appointment_service.get_all_appointments()

    def get_appointment_by_prestation(self, prestation_id):
        return self.appointment_service.get_appointment_by_prestation(prestation_id)

    def get_appointment_by_user(self, user_id):
        return self.appointment_service.get_appointment_by_user(user_id)

    def get_appointment_by_user_and_prestation(self, user_id, prestation_id):
        return self.appointment_service.get_appointment_by_user_and_prestation(user_id, prestation_id)

    def get_appointments_by_status(self, status):
        return self.appointment_service.get_appointments_by_status(status)

    def reassign_appointments_from_user(self, old_user_id, new_user_id):
        return self.appointment_service.reassign_appointments_from_user(old_user_id, new_user_id)

    def update_appointment_status(self, appointment_id, **kwargs):
        return self.appointment_service.update_appointment_status(appointment_id, **kwargs)

    def delete_appointment(self, appointment_id):
        return self.appointment_service.delete_appointment(appointment_id)

    # Prestation CRUD operations
    def create_prestation(self, **kwargs):
        return self.prestation_service.create_prestation(**kwargs)

    def get_prestation_by_id(self, prestation_id):
        return self.prestation_service.get_prestation_by_id(prestation_id)

    def get_all_prestations(self):
        return self.prestation_service.get_all_prestations()

    def get_all_prestations_for_user(self):
        return self.prestation_service.get_all_prestations_for_user()

    def get_prestation_by_name(self, name):
        return self.prestation_service.get_prestation_by_name(name)

    def update_prestation(self, prestation_id, **kwargs):
        return self.prestation_service.update_prestation(prestation_id, **kwargs)

    def delete_prestation(self, prestation_id):
        return self.prestation_service.delete_prestation(prestation_id)
