import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.models.review import Review
from app.models.appointment import Appointment
from app.models.prestation import Prestation


class TestAllRelations(BaseTest):
    def setUp(self):
        super().setUp()
        self.user = User(first_name="John", last_name="Doe",
                         email="john@example.com", address=None, phone_number=None,
                         password="Password123!", is_admin=False)
        self.user2 = User(first_name="Jane", last_name="Smith",
                         email="jane@example.com", address=None, phone_number=None,
                         password="Password123!", is_admin=False)
        self.prestation = Prestation(name="Massage thérapeutique")
        self.save_to_db(self.user, self.user2, self.prestation)

    def test_user_with_reviews_and_appointments(self):
        # Un utilisateur peut avoir à la fois des avis et des rendez-vous
        review = Review(text="Excellent service!", rating=5, user=self.user, prestation=self.prestation)
        appointment = Appointment(subject="Massage suédois", 
                                message="Nouveau rendez-vous", user=self.user, prestation=self.prestation)
        
        # Vérifier les relations
        self.assertEqual(review.user, self.user)
        self.assertEqual(appointment.user, self.user)
        self.assertEqual(review._user_id, self.user.id)
        self.assertEqual(appointment._user_id, self.user.id)

    def test_multiple_users_multiple_entities(self):
        # Plusieurs utilisateurs avec plusieurs entités chacun
        
        # User 1: 2 avis + 1 rendez-vous
        review1_u1 = Review(text="Great massage", rating=5, user=self.user, prestation=self.prestation)
        review2_u1 = Review(text="Good reflexology", rating=4, user=self.user, prestation=self.prestation)
        appointment1_u1 = Appointment(subject="Aromathérapie", 
                                    message="Séance détente", user=self.user, prestation=self.prestation)
        
        # User 2: 1 avis + 2 rendez-vous
        review1_u2 = Review(text="Amazing experience", rating=5, user=self.user2, prestation=self.prestation)
        appointment1_u2 = Appointment(subject="Massage thérapeutique", 
                                    message="Soulager douleurs", user=self.user2, prestation=self.prestation)
        appointment2_u2 = Appointment(subject="Réflexologie", 
                                    message="Bien-être", user=self.user2, prestation=self.prestation)
        
        # Vérifications User 1
        self.assertEqual(review1_u1.user, self.user)
        self.assertEqual(review2_u1.user, self.user)
        self.assertEqual(appointment1_u1.user, self.user)
        
        # Vérifications User 2
        self.assertEqual(review1_u2.user, self.user2)
        self.assertEqual(appointment1_u2.user, self.user2)
        self.assertEqual(appointment2_u2.user, self.user2)

    def test_entity_isolation_between_users(self):
        # Les entités d'un utilisateur n'interfèrent pas avec celles d'un autre
        review_u1 = Review(text="User 1 review", rating=5, user=self.user, prestation=self.prestation)
        review_u2 = Review(text="User 2 review", rating=4, user=self.user2, prestation=self.prestation)
        
        appointment_u1 = Appointment(subject="User 1 appointment", 
                                   message="Message 1", user=self.user, prestation=self.prestation)
        appointment_u2 = Appointment(subject="User 2 appointment", 
                                   message="Message 2", user=self.user2, prestation=self.prestation)
        
        # Vérifier l'isolation
        self.assertNotEqual(review_u1._user_id, review_u2._user_id)
        self.assertNotEqual(appointment_u1._user_id, appointment_u2._user_id)
        self.assertNotEqual(review_u1.id, review_u2.id)
        self.assertNotEqual(appointment_u1.id, appointment_u2.id)

    def test_user_business_scenario(self):
        # Scénario métier: Un client laisse un avis puis prend un nouveau RDV
        
        # 1. Client prend un premier RDV
        first_appointment = Appointment(subject="Massage découverte", 
                                      message="Premier essai", user=self.user, prestation=self.prestation)
        
        # 2. Client satisfait laisse un avis
        review = Review(text="Très satisfait de ma première séance!", 
                       rating=5, user=self.user, prestation=self.prestation)
        
        # 3. Client reprend un RDV pour un autre service
        second_appointment = Appointment(subject="Réflexologie plantaire", 
                                       message="Suite à mon excellent premier RDV", 
                                       user=self.user, prestation=self.prestation)
        
        # Vérifications du parcours client
        self.assertEqual(first_appointment.user, self.user)
        self.assertEqual(review.user, self.user)
        self.assertEqual(second_appointment.user, self.user)
        
        # Vérifier que ce sont bien des entités différentes
        self.assertNotEqual(first_appointment.id, second_appointment.id)
        self.assertNotEqual(first_appointment.subject, second_appointment.subject)

    def test_data_consistency_across_relations(self):
        # Cohérence des données à travers les relations
        review = Review(text="Cohérence test", rating=5, user=self.user, prestation=self.prestation)
        appointment = Appointment(subject="Test cohérence", 
                                message="Message test", user=self.user, prestation=self.prestation)
        
        # Les deux entités pointent vers le même utilisateur
        self.assertEqual(review.user.id, appointment.user.id)
        self.assertEqual(review.user.email, appointment.user.email)
        self.assertEqual(review._user_id, appointment._user_id)

    def test_reassign_entity_to_another_user(self):
        review = Review(text="Initial", rating=5, user=self.user, prestation=self.prestation)
        self.save_to_db(review)
        self.assertEqual(review.user, self.user)
    
        # Réassigner l'avis à un autre utilisateur
        review.user = self.user2
        self.save_to_db(review)
    
        # Les relations devraient être mises à jour correctement
        self.assertEqual(review.user, self.user2)
        self.assertEqual(review._user_id, self.user2.id)

    def test_reassigning_entity_updates_relationships(self):
        # Créer un avis pour le premier utilisateur
        review = Review(text="Initial review", rating=5, user=self.user, prestation=self.prestation)
        self.save_to_db(review)
        
        # Vérifier que l'avis est bien dans la liste du premier utilisateur
        self.assertIn(review, self.user.reviews)
        self.assertEqual(review.user, self.user)
        
        # Réassigner l'avis au second utilisateur
        review.user = self.user2
        
        # L'avis devrait avoir été retiré de l'ancienne liste et ajouté à la nouvelle
        self.assertNotIn(review, self.user.reviews)
        self.assertIn(review, self.user2.reviews)
        self.assertEqual(review.user, self.user2)
        
        # Répéter le même scénario pour les rendez-vous
        appointment = Appointment(subject="Initial appointment", message="Test", user=self.user, prestation=self.prestation)
        self.save_to_db(appointment)
        self.assertIn(appointment, self.user.appointments)
        
        appointment.user = self.user2
        self.save_to_db(appointment)
        self.assertIn(appointment, self.user2.appointments)
        self.assertEqual(appointment.user, self.user2)

    def test_user_reviews_and_appointments_are_separate_lists(self):
        # Un utilisateur peut avoir des avis et des rendez-vous
        review = Review(text="Test distinct lists", rating=5, user=self.user, prestation=self.prestation)
        appointment = Appointment(subject="Test distinct lists", message="Test", user=self.user, prestation=self.prestation)
        self.save_to_db(review, appointment)
        
        # Les deux entités doivent être dans les listes appropriées de l'utilisateur
        self.assertIn(review, self.user.reviews)
        self.assertIn(appointment, self.user.appointments)
        
        # Mais elles ne doivent pas être dans la même liste
        self.assertNotIn(review, self.user.appointments)
        self.assertNotIn(appointment, self.user.reviews)


if __name__ == "__main__":
    unittest.main()
