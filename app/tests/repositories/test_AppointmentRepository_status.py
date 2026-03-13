#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.persistence.AppointmentRepository import AppointmentRepository
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.models.prestation import Prestation


class TestAppointmentRepositoryStatus(BaseTest):
    """Tests unitaires pour AppointmentRepository avec gestion des statuts"""
    
    def setUp(self):
        super().setUp()
        self.appointment_repository = AppointmentRepository()
        
        # Créer des objets de test
        self.user = User(
            first_name='Repository',
            last_name='Test',
            email='repository@example.com',
            password='Password123!',
            is_admin=False
        )
        
        self.prestation = Prestation(name='Repository Test Prestation')
        
        self.save_to_db(self.user, self.prestation)

    def test_create_appointment_default_status(self):
        """Test que les rendez-vous créés ont le statut PENDING par défaut"""
        appointment = Appointment(
            message="Default status test",
            user=self.user,
            prestation=self.prestation
        )
        self.save_to_db(appointment)
        
        self.assertEqual(appointment.status, AppointmentStatus.PENDING)
        self.assertIsNotNone(appointment.id)

    def test_update_appointment_status(self):
        """Test mise à jour du statut via le repository"""
        # Créer un rendez-vous
        appointment = Appointment(
            message="Update status test",
            user=self.user,
            prestation=self.prestation
        )
        self.save_to_db(appointment)
        
        # Mettre à jour le statut
        updated_appointment = self.appointment_repository.update(
            appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        
        self.assertEqual(updated_appointment.status, AppointmentStatus.CONFIRMED)

    def test_get_appointments_by_status(self):
        """Test récupération de rendez-vous par statut"""
        # Créer plusieurs rendez-vous avec différents statuts
        appointments = []
        statuses = [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED]
        
        for i, status in enumerate(statuses):
            appointment = Appointment(
                message=f"Status test {i}",
                user=self.user,
                prestation=self.prestation
            )
            self.save_to_db(appointment)
            
            if status != AppointmentStatus.PENDING:
                self.appointment_repository.update(appointment.id, status=status)
            
            appointments.append(appointment)
        
        # Récupérer tous les rendez-vous de l'utilisateur
        user_appointments = self.appointment_repository.get_by_user_id(self.user.id)
        self.assertEqual(len(user_appointments), 3)
        
        # Vérifier les statuts
        found_statuses = [apt.status for apt in user_appointments]
        for status in statuses:
            self.assertIn(status, found_statuses)

    def test_appointment_status_persistence(self):
        """Test persistance des statuts en base de données"""
        appointment = Appointment(
            message="Persistence test",
            user=self.user,
            prestation=self.prestation
        )
        self.save_to_db(appointment)
        
        # Changer le statut plusieurs fois
        statuses_sequence = [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.COMPLETED
        ]
        
        for status in statuses_sequence:
            self.appointment_repository.update(appointment.id, status=status)
            
            # Récupérer depuis la base pour vérifier
            retrieved = self.appointment_repository.get_by_id(appointment.id)
            self.assertEqual(retrieved.status, status)

    def test_appointment_status_in_relationships(self):
        """Test que les statuts sont correctement gérés dans les relations"""
        # Créer plusieurs rendez-vous
        appointments = []
        for i in range(3):
            appointment = Appointment(
                message=f"Relationship test {i}",
                user=self.user,
                prestation=self.prestation
            )
            self.save_to_db(appointment)
            appointments.append(appointment)
        
        # Mettre à jour avec différents statuts
        statuses = [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]
        for appointment, status in zip(appointments, statuses):
            self.appointment_repository.update(appointment.id, status=status)
        
        # Récupérer via les relations
        user_appointments = self.appointment_repository.get_by_user_id(self.user.id)
        prestation_appointments = self.appointment_repository.get_by_prestation_id(self.prestation.id)
        
        # Vérifier que les statuts sont préservés
        self.assertEqual(len(user_appointments), 3)
        self.assertEqual(len(prestation_appointments), 3)
        
        for appointments_list in [user_appointments, prestation_appointments]:
            found_statuses = [apt.status for apt in appointments_list]
            for status in statuses:
                self.assertIn(status, found_statuses)

    def test_appointment_status_with_reassignment(self):
        """Test que les statuts sont préservés lors de la réassignation"""
        # Créer un utilisateur fantôme
        ghost_user = User(
            first_name='Ghost',
            last_name='User',
            email='deleted@system.local',
            password='Ghost#2025!!',
            is_admin=False
        )
        self.save_to_db(ghost_user)
        
        # Créer un rendez-vous et le confirmer
        appointment = Appointment(
            message="Reassignment status test",
            user=self.user,
            prestation=self.prestation
        )
        self.save_to_db(appointment)
        
        self.appointment_repository.update(appointment.id, status=AppointmentStatus.CONFIRMED)
        
        # Réassigner
        reassigned_count = self.appointment_repository.reassign_appointments_from_user(
            self.user.id,
            ghost_user.id
        )
        
        self.assertEqual(reassigned_count, 1)
        
        # Vérifier que le statut est préservé
        retrieved = self.appointment_repository.get_by_id(appointment.id)
        self.assertEqual(retrieved.status, AppointmentStatus.CONFIRMED)
        self.assertEqual(retrieved.user_id, ghost_user.id)

    def test_appointment_status_validation_at_model_level(self):
        """Test validation des statuts au niveau du modèle"""
        appointment = Appointment(
            message="Model validation test",
            user=self.user,
            prestation=self.prestation
        )
        self.save_to_db(appointment)
        
        # Test avec statut valide
        appointment.status = AppointmentStatus.CONFIRMED
        self.db.session.commit()
        
        # Test avec statut invalide
        with self.assertRaises(ValueError):
            appointment.status = "invalid_status"

    def test_appointment_multiple_status_updates(self):
        """Test mises à jour multiples de statut"""
        appointment = Appointment(
            message="Multiple updates test",
            user=self.user,
            prestation=self.prestation
        )
        self.save_to_db(appointment)
        
        # Effectuer plusieurs mises à jour
        update_sequence = [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.PENDING,
            AppointmentStatus.COMPLETED
        ]
        
        for status in update_sequence:
            updated = self.appointment_repository.update(appointment.id, status=status)
            self.assertEqual(updated.status, status)
            
            # Vérifier en base
            retrieved = self.appointment_repository.get_by_id(appointment.id)
            self.assertEqual(retrieved.status, status)

    def test_appointment_status_query_filtering(self):
        """Test filtrage des requêtes par statut"""
        # Créer des rendez-vous avec différents statuts
        appointments_data = [
            ("Pending appointment", AppointmentStatus.PENDING),
            ("Confirmed appointment 1", AppointmentStatus.CONFIRMED),
            ("Confirmed appointment 2", AppointmentStatus.CONFIRMED),
            ("Cancelled appointment", AppointmentStatus.CANCELLED)
        ]
        
        created_appointments = []
        for message, status in appointments_data:
            appointment = Appointment(
                message=message,
                user=self.user,
                prestation=self.prestation
            )
            self.save_to_db(appointment)
            
            if status != AppointmentStatus.PENDING:
                self.appointment_repository.update(appointment.id, status=status)
            
            created_appointments.append(appointment)
        
        # Récupérer tous les rendez-vous
        all_appointments = self.appointment_repository.get_by_user_id(self.user.id)
        self.assertEqual(len(all_appointments), 4)
        
        # Compter par statut
        status_counts = {}
        for appointment in all_appointments:
            status = appointment.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        self.assertEqual(status_counts[AppointmentStatus.PENDING], 1)
        self.assertEqual(status_counts[AppointmentStatus.CONFIRMED], 2)
        self.assertEqual(status_counts[AppointmentStatus.CANCELLED], 1)

    def test_appointment_status_concurrent_access(self):
        """Test accès concurrent aux statuts"""
        appointment = Appointment(
            message="Concurrent access test",
            user=self.user,
            prestation=self.prestation
        )
        self.save_to_db(appointment)
        
        # Simuler des accès concurrents
        # Premier accès
        apt1 = self.appointment_repository.get_by_id(appointment.id)
        apt1.status = AppointmentStatus.CONFIRMED
        
        # Deuxième accès
        apt2 = self.appointment_repository.get_by_id(appointment.id)
        apt2.status = AppointmentStatus.CANCELLED
        
        # Sauvegarder les deux
        self.db.session.add(apt1)
        self.db.session.add(apt2)
        self.db.session.commit()
        
        # Vérifier le résultat final
        final_appointment = self.appointment_repository.get_by_id(appointment.id)
        # Le dernier commit devrait prévaloir
        self.assertEqual(final_appointment.status, AppointmentStatus.CANCELLED)


if __name__ == '__main__':
    unittest.main()