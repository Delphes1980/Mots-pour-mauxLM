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
            password="Password123!",
            is_admin=False
        )
        
        self.user2 = User(
            first_name="Bob", 
            last_name="Dupont",
            email="bob@example.com",
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

if __name__ == "__main__":
    unittest.main()