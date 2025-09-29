from app.services.UserService import UserService
from app.services.ReviewService import ReviewService
from app.services.AppointmentService import AppointmentService
from app.services.PrestationService import PrestationService


class Facade:
    def __init__(self):
        self.user_service = UserService()
        self.review_service = ReviewService()
        self.appointment_service = AppointmentService()
        self.prestation_service = PrestationService()

    # User CRUD operations
    def create_user(self, **kwargs):
        return self.user_service.create_user(**kwargs)

    def get_user_by_id(self, user_id):
        return self.user_service.get_user_by_id(user_id)

    def get_user_by_email(self, email):
        return self.user_service.get_user_by_email(email)

    def get_all_users(self):
        return self.user_service.get_all_users()

    def update_user(self, user_id, **kwargs):
        return self.user_service.update_user(user_id, **kwargs)

    def delete_user(self, user_id):
        return self.user_service.delete_user(user_id)

    def login(self, email, password):
        return self.user_service.login(email, password)

    # Review CRUD operations
    def create_review(self, **kwargs):
        return self.review_service.create_review(**kwargs)

    def get_review_by_id(self, review_id):
        return self.review_service.get_review_by_id(review_id)

    def get_all_reviews(self):
        return self.review_service.get_all_reviews()

    def get_review_by_prestation(self, prestation_id):
        return self.review_service.get_review_by_prestation(prestation_id)

    def get_review_by_user(self, user_id):
        return self.review_service.get_review_by_user(user_id)

    def update_review(self, **kwargs):
        return self.review_service.update_review(**kwargs)

    def delete_review(self, review_id):
        return self.review_service.delete_review(review_id)

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

    # Prestation CRUD operations
    def create_prestation(self, **kwargs):
        return self.prestation_service.create_prestation(**kwargs)

    def get_prestation_by_id(self, prestation_id):
        return self.prestation_service.get_prestation_by_id(prestation_id)

    def get_all_prestations(self):
        return self.prestation_service.get_all_prestations()

    def get_prestation_by_name(self, name):
        return self.prestation_service.get_prestation_by_name(name)

    def update_prestation(self, **kwargs):
        return self.prestation_service.update_prestation(**kwargs)

    def delete_prestation(self, prestation_id):
        return self.prestation_service.delete_prestation(prestation_id)
