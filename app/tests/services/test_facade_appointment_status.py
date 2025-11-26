#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.services.facade import Facade
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.models.prestation import Prestation
from app.utils import CustomError


class TestFacadeAppointmentStatus(BaseTest):
    """Tests de délégation pour les nouvelles fonctionnalités de statut des rendez-vous"""
    
    def setUp(self):
        super().setUp()
        self.facade = Facade()
        
        # Créer des objets de test
        self.user = User(
            first_name='Facade',
            last_name='Test',
            email='facade@example.com',
            password='Password123!',
            is_admin=False
        )
        
        self.prestation = Prestation(name='Facade Test Prestation')
        
        self.save_to_db(self.user, self.prestation)

    def test_update_appointment_status_delegation(self):
        """Test délégation update_appointment_status"""
        # Créer un rendez-vous
        appointment = self.facade.create_appointment(
            message="Facade delegation test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Mettre à jour le statut via la facade
        updated_appointment = self.facade.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        
        self.assertIsNotNone(updated_appointment)
        self.assertEqual(updated_appointment.status, AppointmentStatus.CONFIRMED)
        self.assertEqual(updated_appointment.id, appointment.id)

    def test_update_appointment_status_all_statuses_delegation(self):
        """Test délégation avec tous les statuts valides"""
        appointment = self.facade.create_appointment(
            message="All statuses test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        valid_statuses = [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.COMPLETED,
            AppointmentStatus.PENDING
        ]
        
        for status in valid_statuses:
            updated = self.facade.update_appointment_status(
                appointment.id,
                status=status
            )
            self.assertEqual(updated.status, status)

    def test_update_appointment_status_error_delegation(self):
        """Test délégation des erreurs"""
        appointment = self.facade.create_appointment(
            message="Error delegation test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Test avec statut invalide
        with self.assertRaises(CustomError) as context:
            self.facade.update_appointment_status(
                appointment.id,
                status="invalid_status"
            )
        
        self.assertEqual(context.exception.status_code, 400)
        
        # Test avec ID invalide
        with self.assertRaises(CustomError) as context:
            self.facade.update_appointment_status(
                "invalid-id",
                status=AppointmentStatus.CONFIRMED
            )
        
        self.assertEqual(context.exception.status_code, 400)

    def test_appointment_workflow_integration_via_facade(self):
        """Test workflow complet via la facade"""
        # 1. Créer un rendez-vous
        appointment = self.facade.create_appointment(
            message="Workflow integration test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Vérifier le statut initial
        self.assertEqual(appointment.status, AppointmentStatus.PENDING)
        
        # 2. Confirmer le rendez-vous
        confirmed = self.facade.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        self.assertEqual(confirmed.status, AppointmentStatus.CONFIRMED)
        
        # 3. Récupérer le rendez-vous pour vérifier
        retrieved = self.facade.get_appointment_by_id(appointment.id)
        self.assertEqual(retrieved.status, AppointmentStatus.CONFIRMED)
        
        # 4. Compléter le rendez-vous
        completed = self.facade.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.COMPLETED
        )
        self.assertEqual(completed.status, AppointmentStatus.COMPLETED)

    def test_appointment_status_with_user_operations_integration(self):
        """Test intégration statuts avec opérations utilisateur"""
        # Créer plusieurs rendez-vous
        appointments = []
        for i in range(3):
            appointment = self.facade.create_appointment(
                message=f"User integration test {i}",
                user_id=self.user.id,
                prestation_id=self.prestation.id
            )
            appointments.append(appointment)
        
        # Mettre à jour avec différents statuts
        statuses = [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]
        for appointment, status in zip(appointments, statuses):
            self.facade.update_appointment_status(appointment.id, status=status)
        
        # Récupérer tous les rendez-vous de l'utilisateur
        user_appointments = self.facade.get_appointment_by_user(self.user.id)
        self.assertEqual(len(user_appointments), 3)
        
        # Vérifier les statuts
        found_statuses = [apt.status for apt in user_appointments]
        for status in statuses:
            self.assertIn(status, found_statuses)

    def test_appointment_status_with_prestation_operations_integration(self):
        """Test intégration statuts avec opérations prestation"""
        # Créer une deuxième prestation
        prestation2 = Prestation(name='Second Facade Prestation')
        self.save_to_db(prestation2)
        
        # Créer des rendez-vous pour les deux prestations
        apt1 = self.facade.create_appointment(
            message="Prestation 1 appointment",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        apt2 = self.facade.create_appointment(
            message="Prestation 2 appointment",
            user_id=self.user.id,
            prestation_id=prestation2.id
        )
        
        # Mettre à jour avec différents statuts
        self.facade.update_appointment_status(apt1.id, status=AppointmentStatus.CONFIRMED)
        self.facade.update_appointment_status(apt2.id, status=AppointmentStatus.CANCELLED)
        
        # Récupérer par prestation
        prestation1_appointments = self.facade.get_appointment_by_prestation(self.prestation.id)
        prestation2_appointments = self.facade.get_appointment_by_prestation(prestation2.id)
        
        self.assertEqual(len(prestation1_appointments), 1)
        self.assertEqual(len(prestation2_appointments), 1)
        
        self.assertEqual(prestation1_appointments[0].status, AppointmentStatus.CONFIRMED)
        self.assertEqual(prestation2_appointments[0].status, AppointmentStatus.CANCELLED)

    def test_appointment_status_with_reassignment_integration(self):
        """Test intégration statuts avec réassignation"""
        # Créer un utilisateur fantôme
        ghost_user = self.facade.create_user(
            first_name='Ghost',
            last_name='User',
            email='deleted@system.local',
            password='Ghost#2025!',
            is_admin=False
        )
        
        # Créer un rendez-vous et le confirmer
        appointment = self.facade.create_appointment(
            message="Reassignment integration test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        self.facade.update_appointment_status(appointment.id, status=AppointmentStatus.CONFIRMED)
        
        # Réassigner les rendez-vous
        reassigned = self.facade.reassign_appointments_from_user(self.user.id, ghost_user.id)
        self.assertEqual(len(reassigned), 1)
        
        # Vérifier que le statut est préservé
        updated_appointment = self.facade.get_appointment_by_id(appointment.id)
        self.assertEqual(updated_appointment.status, AppointmentStatus.CONFIRMED)
        self.assertEqual(updated_appointment.user_id, ghost_user.id)

    def test_appointment_status_persistence_via_facade(self):
        """Test persistance des statuts via la facade"""
        appointment = self.facade.create_appointment(
            message="Persistence via facade test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Effectuer plusieurs mises à jour
        update_sequence = [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.PENDING,
            AppointmentStatus.COMPLETED
        ]
        
        for status in update_sequence:
            # Mettre à jour
            self.facade.update_appointment_status(appointment.id, status=status)
            
            # Vérifier immédiatement
            retrieved = self.facade.get_appointment_by_id(appointment.id)
            self.assertEqual(retrieved.status, status)

    def test_appointment_status_error_handling_via_facade(self):
        """Test gestion d'erreurs via la facade"""
        appointment = self.facade.create_appointment(
            message="Error handling via facade test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Test avec différents types d'erreurs
        error_cases = [
            # (appointment_id, status, expected_status_code)
            ("invalid-id", AppointmentStatus.CONFIRMED, 400),
            ("12345678-1234-1234-1234-123456789012", AppointmentStatus.CONFIRMED, 404),
            (appointment.id, "invalid_status", 400),
            (appointment.id, None, 400)
        ]
        
        for apt_id, status, expected_code in error_cases:
            with self.assertRaises(CustomError) as context:
                if status is None:
                    self.facade.update_appointment_status(apt_id)
                else:
                    self.facade.update_appointment_status(apt_id, status=status)
            
            self.assertEqual(context.exception.status_code, expected_code)

    def test_appointment_status_with_all_appointments_integration(self):
        """Test intégration avec get_all_appointments"""
        # Créer plusieurs rendez-vous avec différents statuts
        appointments_data = [
            ("Pending appointment", AppointmentStatus.PENDING),
            ("Confirmed appointment", AppointmentStatus.CONFIRMED),
            ("Cancelled appointment", AppointmentStatus.CANCELLED),
            ("Completed appointment", AppointmentStatus.COMPLETED)
        ]
        
        created_appointments = []
        for message, status in appointments_data:
            appointment = self.facade.create_appointment(
                message=message,
                user_id=self.user.id,
                prestation_id=self.prestation.id
            )
            
            if status != AppointmentStatus.PENDING:
                self.facade.update_appointment_status(appointment.id, status=status)
            
            created_appointments.append(appointment)
        
        # Récupérer tous les rendez-vous
        all_appointments = self.facade.get_all_appointments()
        
        # Filtrer ceux de notre utilisateur
        user_appointments = [apt for apt in all_appointments if apt.user_id == self.user.id]
        self.assertEqual(len(user_appointments), 4)
        
        # Vérifier que tous les statuts sont présents
        found_statuses = [apt.status for apt in user_appointments]
        for _, expected_status in appointments_data:
            self.assertIn(expected_status, found_statuses)

    def test_appointment_status_consistency_across_methods(self):
        """Test cohérence des statuts à travers toutes les méthodes"""
        appointment = self.facade.create_appointment(
            message="Consistency test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Mettre à jour le statut
        self.facade.update_appointment_status(appointment.id, status=AppointmentStatus.CONFIRMED)
        
        # Vérifier via toutes les méthodes de récupération
        methods_to_test = [
            lambda: self.facade.get_appointment_by_id(appointment.id),
            lambda: self.facade.get_appointment_by_user(self.user.id)[0],
            lambda: self.facade.get_appointment_by_prestation(self.prestation.id)[0],
            lambda: self.facade.get_appointment_by_user_and_prestation(self.user.id, self.prestation.id)[0]
        ]
        
        for method in methods_to_test:
            retrieved = method()
            self.assertEqual(retrieved.status, AppointmentStatus.CONFIRMED)


if __name__ == '__main__':
    unittest.main()