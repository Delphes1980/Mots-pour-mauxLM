#!/usr/bin/env python3
"""
Test général de toutes les entités et relations
==============================================

Ce test valide :
- Création de toutes les entités (User, Prestation, Review, Appointment)
- Toutes les relations bidirectionnelles
- Opérations CRUD complètes
- Intégrité des données

Utilise la base de données: therapie_test
"""

import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.models.prestation import Prestation
from app.models.review import Review
from app.models.appointment import Appointment

class TestAllEntitiesRelationships(BaseTest):
    """Test complet de toutes les entités et relations"""
    
    def setUp(self):
        super().setUp()
        
        # Création des entités de base
        self.user1 = User(
            first_name="Alice",
            last_name="Martin",
            email="alice@example.com",
            address=None,
            phone_number=None,
            password="Password123!",
            is_admin=False
        )
        
        self.user2 = User(
            first_name="Bob", 
            last_name="Dupont",
            email="bob@example.com",
            address=None,
            phone_number=None,
            password="Password123!",
            is_admin=True
        )
        
        self.prestation1 = Prestation(name="Massage suédois")
        self.prestation2 = Prestation(name="Réflexologie plantaire")
        
        # Sauvegarder les entités de base
        self.save_to_db(self.user1, self.user2, self.prestation1, self.prestation2)
    
    def test_complete_entities_creation(self):
        """Test de création de toutes les entités"""
        # Vérifier que toutes les entités sont créées
        self.assertIsNotNone(self.user1.id)
        self.assertIsNotNone(self.user2.id)
        self.assertIsNotNone(self.prestation1.id)
        self.assertIsNotNone(self.prestation2.id)
        
        # Vérifier les propriétés
        self.assertEqual(self.user1.email, "alice@example.com")
        self.assertEqual(self.prestation1.name, "Massage suédois")
        self.assertFalse(self.user1.is_admin)
        self.assertTrue(self.user2.is_admin)
    
    def test_review_relationships(self):
        """Test des relations Review avec User et Prestation"""
        # Créer des avis
        review1 = Review(
            text="Excellent massage, très relaxant !",
            rating=5,
            user=self.user1,
            prestation=self.prestation1
        )
        
        review2 = Review(
            text="Très bonne réflexologie, je recommande.",
            rating=4,
            user=self.user2,
            prestation=self.prestation2
        )
        
        self.save_to_db(review1, review2)
        
        # Vérifier les relations directes
        self.assertEqual(review1.user, self.user1)
        self.assertEqual(review1.prestation, self.prestation1)
        self.assertEqual(review2.user, self.user2)
        self.assertEqual(review2.prestation, self.prestation2)
        
        # Vérifier les relations inverses
        self.assertIn(review1, self.user1.reviews)
        self.assertIn(review1, self.prestation1.reviews)
        self.assertIn(review2, self.user2.reviews)
        self.assertIn(review2, self.prestation2.reviews)
    
    def test_appointment_relationships(self):
        """Test des relations Appointment avec User et Prestation"""
        # Créer des rendez-vous
        appointment1 = Appointment(
            subject="RDV Massage suédois",
            message="Je souhaite un rendez-vous pour un massage relaxant",
            user=self.user1,
            prestation=self.prestation1
        )
        
        appointment2 = Appointment(
            subject="RDV Réflexologie",
            message="Rendez-vous pour soulager mes pieds",
            user=self.user1,
            prestation=self.prestation2
        )
        
        self.save_to_db(appointment1, appointment2)
        
        # Vérifier les relations directes
        self.assertEqual(appointment1.user, self.user1)
        self.assertEqual(appointment1.prestation, self.prestation1)
        self.assertEqual(appointment2.user, self.user1)
        self.assertEqual(appointment2.prestation, self.prestation2)
        
        # Vérifier les relations inverses
        self.assertIn(appointment1, self.user1.appointments)
        self.assertIn(appointment2, self.user1.appointments)
        self.assertIn(appointment1, self.prestation1.appointments)
        self.assertIn(appointment2, self.prestation2.appointments)
    
    def test_multiple_users_same_prestation(self):
        """Test de plusieurs utilisateurs pour la même prestation"""
        # Plusieurs avis pour la même prestation
        review1 = Review(
            text="Super massage !",
            rating=5,
            user=self.user1,
            prestation=self.prestation1
        )
        
        review2 = Review(
            text="Très bien aussi !",
            rating=4,
            user=self.user2,
            prestation=self.prestation1
        )
        
        # Plusieurs rendez-vous pour la même prestation
        appointment1 = Appointment(
            subject="RDV Alice",
            message="Rendez-vous d'Alice",
            user=self.user1,
            prestation=self.prestation1
        )
        
        appointment2 = Appointment(
            subject="RDV Bob",
            message="Rendez-vous de Bob",
            user=self.user2,
            prestation=self.prestation1
        )
        
        self.save_to_db(review1, review2, appointment1, appointment2)
        
        # Vérifier que la prestation a bien les deux avis et rendez-vous
        self.assertEqual(len(self.prestation1.reviews), 2)
        self.assertEqual(len(self.prestation1.appointments), 2)
        
        # Vérifier que chaque utilisateur a ses propres relations
        self.assertIn(review1, self.user1.reviews)
        self.assertIn(review2, self.user2.reviews)
        self.assertIn(appointment1, self.user1.appointments)
        self.assertIn(appointment2, self.user2.appointments)
    
    def test_user_multiple_prestations(self):
        """Test d'un utilisateur avec plusieurs prestations"""
        # Un utilisateur prend plusieurs prestations
        review1 = Review(
            text="Massage excellent",
            rating=5,
            user=self.user1,
            prestation=self.prestation1
        )
        
        review2 = Review(
            text="Réflexologie parfaite",
            rating=5,
            user=self.user1,
            prestation=self.prestation2
        )
        
        appointment1 = Appointment(
            subject="RDV Massage",
            message="Pour le massage",
            user=self.user1,
            prestation=self.prestation1
        )
        
        appointment2 = Appointment(
            subject="RDV Réflexologie",
            message="Pour la réflexologie",
            user=self.user1,
            prestation=self.prestation2
        )
        
        self.save_to_db(review1, review2, appointment1, appointment2)
        
        # Vérifier que l'utilisateur a bien toutes ses relations
        self.assertEqual(len(self.user1.reviews), 2)
        self.assertEqual(len(self.user1.appointments), 2)
        
        # Vérifier la diversité des prestations
        prestations_reviews = [r.prestation for r in self.user1.reviews]
        prestations_appointments = [a.prestation for a in self.user1.appointments]
        
        self.assertIn(self.prestation1, prestations_reviews)
        self.assertIn(self.prestation2, prestations_reviews)
        self.assertIn(self.prestation1, prestations_appointments)
        self.assertIn(self.prestation2, prestations_appointments)
    
    def test_crud_operations_all_entities(self):
        """Test des opérations CRUD sur toutes les entités"""
        # CREATE - déjà testé dans setUp
        
        # READ
        user_from_db = self.db.session.query(User).filter_by(email="alice@example.com").first()
        prestation_from_db = self.db.session.query(Prestation).filter_by(name="Massage suédois").first()
        
        self.assertEqual(user_from_db.first_name, "Alice")
        self.assertEqual(prestation_from_db.name, "Massage suédois")
        
        # UPDATE
        self.user1.first_name = "Alice-Updated"
        self.prestation1.name = "Massage suédois - Mis à jour"
        self.db.session.commit()
        
        updated_user = self.db.session.query(User).filter_by(email="alice@example.com").first()
        updated_prestation = self.db.session.query(Prestation).filter_by(name="Massage suédois - Mis à jour").first()
        
        self.assertEqual(updated_user.first_name, "Alice-Updated")
        self.assertEqual(updated_prestation.name, "Massage suédois - Mis à jour")
        
        # DELETE sera géré par tearDown automatiquement
    
    def test_users_with_address_and_phone(self):
        """Test des utilisateurs avec adresse et téléphone"""
        # Créer des utilisateurs avec différentes combinaisons
        user_with_both = User(
            first_name="Claire",
            last_name="Dubois",
            email="claire@example.com",
            address="123 Rue de la Paix, Paris",
            phone_number="0123456789",
            password="Password123!"
        )
        
        user_with_address_only = User(
            first_name="David",
            last_name="Martin",
            email="david@example.com",
            address="456 Avenue des Champs, Lyon",
            phone_number=None,
            password="Password123!"
        )
        
        user_with_phone_only = User(
            first_name="Emma",
            last_name="Leroy",
            email="emma@example.com",
            address=None,
            phone_number="+33 1 23 45 67 89",
            password="Password123!"
        )
        
        self.save_to_db(user_with_both, user_with_address_only, user_with_phone_only)
        
        # Vérifier la persistance en base
        db_user_both = self.db.session.query(User).filter_by(email="claire@example.com").first()
        db_user_address = self.db.session.query(User).filter_by(email="david@example.com").first()
        db_user_phone = self.db.session.query(User).filter_by(email="emma@example.com").first()
        
        # Vérifications utilisateur avec les deux
        self.assertEqual(db_user_both.address, "123 Rue de la Paix, Paris")
        self.assertEqual(db_user_both.phone_number, "0123456789")
        
        # Vérifications utilisateur avec adresse seulement
        self.assertEqual(db_user_address.address, "456 Avenue des Champs, Lyon")
        self.assertIsNone(db_user_address.phone_number)
        
        # Vérifications utilisateur avec téléphone seulement
        self.assertIsNone(db_user_phone.address)
        self.assertEqual(db_user_phone.phone_number, "+33 1 23 45 67 89")
    
    def test_user_contact_info_in_relationships(self):
        """Test que les infos de contact sont préservées dans les relations"""
        # Créer un utilisateur avec infos complètes
        user_complete = User(
            first_name="Sophie",
            last_name="Bernard",
            email="sophie@example.com",
            address="789 Boulevard Saint-Germain, Paris",
            phone_number="01-23-45-67-89",
            password="Password123!"
        )
        
        self.save_to_db(user_complete)
        
        # Créer des relations avec cet utilisateur
        review = Review(
            text="Excellent service, très professionnel",
            rating=5,
            user=user_complete,
            prestation=self.prestation1
        )
        
        appointment = Appointment(
            subject="RDV Massage complet",
            message="Rendez-vous pour massage thérapeutique",
            user=user_complete,
            prestation=self.prestation1
        )
        
        self.save_to_db(review, appointment)
        
        # Vérifier que les infos de contact sont accessibles via les relations
        self.assertEqual(review.user.address, "789 Boulevard Saint-Germain, Paris")
        self.assertEqual(review.user.phone_number, "01-23-45-67-89")
        self.assertEqual(appointment.user.address, "789 Boulevard Saint-Germain, Paris")
        self.assertEqual(appointment.user.phone_number, "01-23-45-67-89")
        
        # Vérifier via les relations inverses
        user_from_review = self.prestation1.reviews[0].user
        user_from_appointment = self.prestation1.appointments[0].user
        
        self.assertEqual(user_from_review.address, "789 Boulevard Saint-Germain, Paris")
        self.assertEqual(user_from_review.phone_number, "01-23-45-67-89")
        self.assertEqual(user_from_appointment.address, "789 Boulevard Saint-Germain, Paris")
        self.assertEqual(user_from_appointment.phone_number, "01-23-45-67-89")
    
    def test_update_user_contact_info(self):
        """Test de mise à jour des informations de contact"""
        # Créer un utilisateur sans infos de contact
        user = User(
            first_name="Thomas",
            last_name="Petit",
            email="thomas@example.com",
            address=None,
            phone_number=None,
            password="Password123!"
        )
        
        self.save_to_db(user)
        
        # Ajouter les infos de contact
        user.address = "321 Rue Neuve, Marseille"
        user.phone_number = "04 91 23 45 67"
        self.db.session.commit()
        
        # Vérifier la mise à jour
        updated_user = self.db.session.query(User).filter_by(email="thomas@example.com").first()
        self.assertEqual(updated_user.address, "321 Rue Neuve, Marseille")
        self.assertEqual(updated_user.phone_number, "04 91 23 45 67")
        
        # Modifier les infos
        user.address = "654 Place Bellecour, Lyon"
        user.phone_number = "+33 4 78 12 34 56"
        self.db.session.commit()
        
        # Vérifier les modifications
        modified_user = self.db.session.query(User).filter_by(email="thomas@example.com").first()
        self.assertEqual(modified_user.address, "654 Place Bellecour, Lyon")
        self.assertEqual(modified_user.phone_number, "+33 4 78 12 34 56")
        
        # Supprimer les infos (remettre à None)
        user.address = None
        user.phone_number = None
        self.db.session.commit()
        
        # Vérifier la suppression
        final_user = self.db.session.query(User).filter_by(email="thomas@example.com").first()
        self.assertIsNone(final_user.address)
        self.assertIsNone(final_user.phone_number)

if __name__ == "__main__":
    unittest.main()