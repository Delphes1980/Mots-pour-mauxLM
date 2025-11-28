#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.models.appointment import Appointment
from app.models.user import User
from app.models.prestation import Prestation
from app.persistence.AppointmentRepository import AppointmentRepository


class TestAppointmentRepositoryDelete(BaseTest):
    """Tests pour la suppression de rendez-vous dans AppointmentRepository"""
    
    def setUp(self):
        super().setUp()
        self.appointment_repo = AppointmentRepository()
        # Forcer l'utilisation de l'instance DB de test
        self.appointment_repo.db = self.db
        
        # Créer des données de test
        self.user = User(
            first_name="Repository",
            last_name="Delete",
            email="repo_delete@example.com",
            password="Password123!",
            address=None,
            phone_number=None
        )
        self.db.session.add(self.user)
        
        self.prestation = Prestation(name="Repository Delete Test")
        self.db.session.add(self.prestation)
        
        self.db.session.commit()

    def test_delete_appointment_success(self):
        """Test suppression réussie via repository"""
        # Créer un rendez-vous
        appointment = Appointment(
            message="Repository delete test",
            user=self.user,
            prestation=self.prestation
        )
        self.save_to_db(appointment)
        appointment_id = appointment.id
        
        # Vérifier qu'il existe
        found_appointment = self.appointment_repo.get_by_id(appointment_id)
        self.assertIsNotNone(found_appointment)
        
        # Supprimer
        result = self.appointment_repo.delete(appointment_id)
        self.assertTrue(result)
        
        # Vérifier qu'il n'existe plus
        deleted_appointment = self.appointment_repo.get_by_id(appointment_id)
        self.assertIsNone(deleted_appointment)

    def test_delete_appointment_not_found(self):
        """Test suppression d'un rendez-vous inexistant"""
        fake_id = '12345678-1234-1234-1234-123456789012'
        
        # Tenter de supprimer un rendez-vous inexistant
        result = self.appointment_repo.delete(fake_id)
        
        # Le repository doit retourner False ou gérer l'erreur
        self.assertFalse(result)

    def test_delete_appointment_impact_on_get_all(self):
        """Test impact de la suppression sur get_all()"""
        # Créer plusieurs rendez-vous
        appointment1 = Appointment(message="Test 1", user=self.user, prestation=self.prestation)
        appointment2 = Appointment(message="Test 2", user=self.user, prestation=self.prestation)
        self.save_to_db(appointment1, appointment2)
        
        # Vérifier qu'il y en a 2
        all_appointments = self.appointment_repo.get_all()
        self.assertEqual(len(all_appointments), 2)
        
        # Supprimer un
        result = self.appointment_repo.delete(appointment1.id)
        self.assertTrue(result)
        
        # Vérifier qu'il n'en reste qu'un
        all_appointments_after = self.appointment_repo.get_all()
        self.assertEqual(len(all_appointments_after), 1)
        self.assertEqual(all_appointments_after[0].id, appointment2.id)

    def test_delete_appointment_impact_on_user_relationships(self):
        """Test impact de la suppression sur les relations utilisateur"""
        # Créer plusieurs rendez-vous pour le même utilisateur
        appointment1 = Appointment(message="User relation 1", user=self.user, prestation=self.prestation)
        appointment2 = Appointment(message="User relation 2", user=self.user, prestation=self.prestation)
        self.save_to_db(appointment1, appointment2)
        
        # Vérifier les rendez-vous de l'utilisateur
        user_appointments = self.appointment_repo.get_by_user_id(self.user.id)
        self.assertEqual(len(user_appointments), 2)
        
        # Supprimer un rendez-vous
        self.appointment_repo.delete(appointment1.id)
        
        # Vérifier que l'utilisateur n'a plus qu'un rendez-vous
        user_appointments_after = self.appointment_repo.get_by_user_id(self.user.id)
        self.assertEqual(len(user_appointments_after), 1)
        self.assertEqual(user_appointments_after[0].id, appointment2.id)

    def test_delete_appointment_impact_on_prestation_relationships(self):
        """Test impact de la suppression sur les relations prestation"""
        # Créer plusieurs rendez-vous pour la même prestation
        appointment1 = Appointment(message="Prestation relation 1", user=self.user, prestation=self.prestation)
        appointment2 = Appointment(message="Prestation relation 2", user=self.user, prestation=self.prestation)
        self.save_to_db(appointment1, appointment2)
        
        # Vérifier les rendez-vous de la prestation
        prestation_appointments = self.appointment_repo.get_by_prestation_id(self.prestation.id)
        self.assertEqual(len(prestation_appointments), 2)
        
        # Supprimer un rendez-vous
        self.appointment_repo.delete(appointment1.id)
        
        # Vérifier que la prestation n'a plus qu'un rendez-vous
        prestation_appointments_after = self.appointment_repo.get_by_prestation_id(self.prestation.id)
        self.assertEqual(len(prestation_appointments_after), 1)
        self.assertEqual(prestation_appointments_after[0].id, appointment2.id)

    def test_delete_appointment_multiple_times(self):
        """Test suppression multiple du même rendez-vous"""
        appointment = Appointment(message="Multiple delete", user=self.user, prestation=self.prestation)
        self.save_to_db(appointment)
        
        # Première suppression
        result1 = self.appointment_repo.delete(appointment.id)
        self.assertTrue(result1)
        
        # Deuxième suppression du même rendez-vous
        result2 = self.appointment_repo.delete(appointment.id)
        self.assertFalse(result2)

    def test_delete_appointment_inheritance_from_base_repository(self):
        """Test que la suppression utilise bien BaseRepository"""
        appointment = Appointment(message="Inheritance test", user=self.user, prestation=self.prestation)
        self.save_to_db(appointment)
        
        # Vérifier que la méthode delete existe (héritée de BaseRepository)
        self.assertTrue(hasattr(self.appointment_repo, 'delete'))
        self.assertTrue(callable(getattr(self.appointment_repo, 'delete')))
        
        # Utiliser la méthode héritée
        result = self.appointment_repo.delete(appointment.id)
        self.assertTrue(result)
        
        # Vérifier que le rendez-vous n'existe plus
        deleted_appointment = self.appointment_repo.get_by_id(appointment.id)
        self.assertIsNone(deleted_appointment)

    def test_delete_appointment_database_consistency(self):
        """Test cohérence de la base de données après suppression"""
        # Créer un rendez-vous
        appointment = Appointment(message="DB consistency", user=self.user, prestation=self.prestation)
        self.save_to_db(appointment)
        
        # Vérifier l'état initial
        initial_count = len(self.appointment_repo.get_all())
        
        # Supprimer
        self.appointment_repo.delete(appointment.id)
        
        # Vérifier que le count a diminué de 1
        final_count = len(self.appointment_repo.get_all())
        self.assertEqual(final_count, initial_count - 1)
        
        # Vérifier que l'utilisateur et la prestation existent toujours
        user_still_exists = self.db.session.get(User, self.user.id)
        prestation_still_exists = self.db.session.get(Prestation, self.prestation.id)
        
        self.assertIsNotNone(user_still_exists)
        self.assertIsNotNone(prestation_still_exists)

    def test_delete_appointment_transaction_behavior(self):
        """Test comportement transactionnel de la suppression"""
        appointment = Appointment(message="Transaction test", user=self.user, prestation=self.prestation)
        self.save_to_db(appointment)
        
        # La suppression doit être immédiatement visible dans la même transaction
        result = self.appointment_repo.delete(appointment.id)
        self.assertTrue(result)
        
        # Vérifier immédiatement
        deleted_appointment = self.appointment_repo.get_by_id(appointment.id)
        self.assertIsNone(deleted_appointment)


if __name__ == '__main__':
    unittest.main()