import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment
from app.models.review import Review


class TestAllRelationships(BaseTest):
    def setUp(self):
        super().setUp()
        self.user1 = User(first_name="John", last_name="Doe",
                         email="john@example.com", address=None, phone_number=None,
                         password="Password123!", is_admin=False)
        self.user2 = User(first_name="Jane", last_name="Smith",
                         email="jane@example.com", address=None, phone_number=None,
                         password="Password456!", is_admin=False)
        self.prestation1 = Prestation(name="Massage suédois")
        self.prestation2 = Prestation(name="Réflexologie plantaire")
        self.prestation3 = Prestation(name="Aromathérapie")
        self.save_to_db(self.user1, self.user2, self.prestation1, self.prestation2, self.prestation3)

    def test_complete_user_journey(self):
        # Parcours complet : RDV → Avis → Nouveau RDV
        
        # 1. Utilisateur prend un RDV pour une prestation
        appointment1 = Appointment(user=self.user1, message="Découverte du massage suédois", 
                                 prestation=self.prestation1)
        
        # 2. Utilisateur satisfait laisse un avis
        review = Review(text="Excellent premier massage, très relaxant!", 
                       rating=5, user=self.user1, prestation=self.prestation1)
        
        # 3. Utilisateur reprend RDV pour une autre prestation
        appointment2 = Appointment(user=self.user1, message="Suite à mon excellent massage", 
                                 prestation=self.prestation2)
        
        # Vérifications du parcours
        self.assertEqual(appointment1.user, self.user1)
        self.assertEqual(appointment1.prestation, self.prestation1)
        self.assertEqual(review.user, self.user1)
        self.assertEqual(review.prestation, self.prestation1)
        self.assertEqual(appointment2.user, self.user1)
        self.assertEqual(appointment2.prestation, self.prestation2)

    def test_multiple_users_multiple_prestations(self):
        # Plusieurs utilisateurs, plusieurs prestations, plusieurs services
        
        # User1: 2 RDV différents + 1 avis
        apt1_u1 = Appointment(user=self.user1, message="Détente", prestation=self.prestation1)
        apt2_u1 = Appointment(user=self.user1, message="Bien-être", prestation=self.prestation3)
        review_u1 = Review(text="Service parfait", rating=5, 
                          user=self.user1, prestation=self.prestation1)
        
        # User2: 1 RDV + 2 avis différents
        apt1_u2 = Appointment(user=self.user2, message="Soulager fatigue", prestation=self.prestation2)
        review1_u2 = Review(text="Très professionnel", rating=4, 
                           user=self.user2, prestation=self.prestation2)
        review2_u2 = Review(text="Aromathérapie apaisante", rating=5, 
                           user=self.user2, prestation=self.prestation3)
        
        # Vérifications User1
        self.assertEqual(apt1_u1.user, self.user1)
        self.assertEqual(apt2_u1.user, self.user1)
        self.assertEqual(review_u1.user, self.user1)
        
        # Vérifications User2
        self.assertEqual(apt1_u2.user, self.user2)
        self.assertEqual(review1_u2.user, self.user2)
        self.assertEqual(review2_u2.user, self.user2)
        
        # Vérifications prestations
        self.assertEqual(apt1_u1.prestation, self.prestation1)
        self.assertEqual(apt2_u1.prestation, self.prestation3)
        self.assertEqual(review_u1.prestation, self.prestation1)
        self.assertEqual(apt1_u2.prestation, self.prestation2)
        self.assertEqual(review1_u2.prestation, self.prestation2)
        self.assertEqual(review2_u2.prestation, self.prestation3)

    def test_prestation_popularity_analysis(self):
        # Analyse de popularité des prestations
        
        # Prestation1: 2 RDV + 2 avis
        Appointment(user=self.user1, message="Test", prestation=self.prestation1)
        Appointment(user=self.user2, message="Test", prestation=self.prestation1)
        Review(text="Bien", rating=4, user=self.user1, prestation=self.prestation1)
        Review(text="Très bien", rating=5, user=self.user2, prestation=self.prestation1)
        
        # Prestation2: 1 RDV + 1 avis
        Appointment(user=self.user1, message="Test", prestation=self.prestation2)
        Review(text="Correct", rating=3, user=self.user1, prestation=self.prestation2)
        
        # Prestation3: 1 avis seulement
        Review(text="Parfait", rating=5, user=self.user2, prestation=self.prestation3)
        
        # Vérifications (toutes les entités créées avec succès)
        self.assertIsNotNone(self.prestation1.id)
        self.assertIsNotNone(self.prestation2.id)
        self.assertIsNotNone(self.prestation3.id)

    def test_data_consistency_across_all_relations(self):
        # Cohérence des données à travers toutes les relations
        
        appointment = Appointment(user=self.user1, message="Message test", prestation=self.prestation1)
        review = Review(text="Test cohérence", rating=4, 
                       user=self.user1, prestation=self.prestation1)
        
        # Même utilisateur dans les deux entités
        self.assertEqual(appointment.user.id, review.user.id)
        self.assertEqual(appointment.user.email, review.user.email)
        self.assertEqual(appointment._user_id, review._user_id)
        
        # Même prestation dans les deux entités
        self.assertEqual(appointment.prestation.id, review.prestation.id)
        self.assertEqual(appointment.prestation.name, review.prestation.name)
        self.assertEqual(appointment._prestation_id, review._prestation_id)

    def test_business_scenario_customer_loyalty(self):
        # Scénario métier: Fidélité client
        
        # Client fidèle: plusieurs prestations, plusieurs avis positifs
        services = [
            (self.prestation1, "Massage suédois", "Première découverte"),
            (self.prestation2, "Réflexologie", "Après le massage"),
            (self.prestation3, "Aromathérapie", "Compléter les soins")
        ]
        
        appointments = []
        reviews = []
        
        for i, (prestation, _, message) in enumerate(services, 1):
            # RDV pour chaque prestation
            apt = Appointment(user=self.user1, message=message, prestation=prestation)
            appointments.append(apt)
            
            # Avis positif pour chaque prestation
            review = Review(text=f"Excellent service {i}/3", rating=5, 
                           user=self.user1, prestation=prestation)
            reviews.append(review)
        
        # Vérifications fidélité
        for apt, review in zip(appointments, reviews):
            self.assertEqual(apt.user, self.user1)
            self.assertEqual(review.user, self.user1)
            self.assertEqual(apt.prestation, review.prestation)
        
        # Vérifier unicité des entités
        apt_ids = [apt.id for apt in appointments]
        review_ids = [r.id for r in reviews]
        self.assertEqual(len(apt_ids), len(set(apt_ids)))
        self.assertEqual(len(review_ids), len(set(review_ids)))

    def test_entity_isolation_between_users(self):
        # Isolation des entités entre utilisateurs
        
        # Entités User1
        apt_u1 = Appointment(user=self.user1, message="Message U1", prestation=self.prestation1)
        review_u1 = Review(text="User1 avis", rating=5, 
                          user=self.user1, prestation=self.prestation1)
        
        # Entités User2
        apt_u2 = Appointment(user=self.user2, message="Message U2", prestation=self.prestation2)
        review_u2 = Review(text="User2 avis", rating=4, 
                          user=self.user2, prestation=self.prestation2)
        
        # Vérifier isolation utilisateurs
        self.assertNotEqual(apt_u1.user.id, apt_u2.user.id)
        self.assertNotEqual(review_u1.user.id, review_u2.user.id)
        self.assertNotEqual(apt_u1._user_id, apt_u2._user_id)
        self.assertNotEqual(review_u1._user_id, review_u2._user_id)
        
        # Vérifier isolation prestations
        self.assertNotEqual(apt_u1.prestation.id, apt_u2.prestation.id)
        self.assertNotEqual(review_u1.prestation.id, review_u2.prestation.id)
        
        # Vérifier isolation entités
        self.assertNotEqual(apt_u1.id, apt_u2.id)
        self.assertNotEqual(review_u1.id, review_u2.id)


if __name__ == "__main__":
    unittest.main()