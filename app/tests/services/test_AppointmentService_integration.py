#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.services.AppointmentService import AppointmentService
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.models.prestation import Prestation
from app.utils import CustomError


class TestAppointmentServiceIntegration(BaseTest):
    """Tests d'intégration pour AppointmentService avec les nouvelles fonctionnalités"""
    
    def setUp(self):
        super().setUp()
        self.appointment_service = AppointmentService()
        
        # Créer des objets de test
        self.user = User(
            first_name='Integration',
            last_name='Test',
            email='integration@example.com',
            password='Password123!',
            is_admin=False
        )
        
        self.prestation = Prestation(name='Integration Prestation')
        
        self.save_to_db(self.user, self.prestation)

    def test_create_appointment_with_status_integration(self):
        """Test création de rendez-vous avec statut par défaut"""
        appointment = self.appointment_service.create_appointment(
            message="Integration test message",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Vérifier que le statut par défaut est PENDING
        self.assertEqual(appointment.status, AppointmentStatus.PENDING)
        self.assertIsNotNone(appointment.id)
        
        # Vérifier en base de données
        retrieved = self.appointment_service.get_appointment_by_id(appointment.id)
        self.assertEqual(retrieved.status, AppointmentStatus.PENDING)

    def test_appointment_lifecycle_integration(self):
        """Test cycle de vie complet d'un rendez-vous"""
        # 1. Création
        appointment = self.appointment_service.create_appointment(
            message="Lifecycle test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        self.assertEqual(appointment.status, AppointmentStatus.PENDING)
        
        # 2. Confirmation
        confirmed = self.appointment_service.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        self.assertEqual(confirmed.status, AppointmentStatus.CONFIRMED)
        
        # 3. Completion
        completed = self.appointment_service.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.COMPLETED
        )
        self.assertEqual(completed.status, AppointmentStatus.COMPLETED)
        
        # Vérifier la persistance
        final = self.appointment_service.get_appointment_by_id(appointment.id)
        self.assertEqual(final.status, AppointmentStatus.COMPLETED)

    def test_appointment_cancellation_workflow_integration(self):
        """Test workflow d'annulation de rendez-vous"""
        # Créer un rendez-vous
        appointment = self.appointment_service.create_appointment(
            message="Cancellation test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Confirmer d'abord
        self.appointment_service.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        
        # Puis annuler
        cancelled = self.appointment_service.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.CANCELLED
        )
        
        self.assertEqual(cancelled.status, AppointmentStatus.CANCELLED)
        
        # Vérifier qu'on peut récupérer les rendez-vous annulés
        user_appointments = self.appointment_service.get_appointment_by_user(self.user.id)
        cancelled_appointments = [apt for apt in user_appointments if apt.status == AppointmentStatus.CANCELLED]
        self.assertEqual(len(cancelled_appointments), 1)

    def test_multiple_appointments_same_user_integration(self):
        """Test gestion de plusieurs rendez-vous pour le même utilisateur"""
        # Créer plusieurs rendez-vous
        appointments = []
        for i in range(3):
            appointment = self.appointment_service.create_appointment(
                message=f"Multiple test {i}",
                user_id=self.user.id,
                prestation_id=self.prestation.id
            )
            appointments.append(appointment)
        
        # Mettre à jour avec différents statuts
        statuses = [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]
        for i, appointment in enumerate(appointments):
            self.appointment_service.update_appointment_status(
                appointment.id,
                status=statuses[i]
            )
        
        # Vérifier tous les rendez-vous de l'utilisateur
        user_appointments = self.appointment_service.get_appointment_by_user(self.user.id)
        self.assertEqual(len(user_appointments), 3)
        
        # Vérifier les statuts
        appointment_statuses = [apt.status for apt in user_appointments]
        for status in statuses:
            self.assertIn(status, appointment_statuses)

    def test_appointment_reassignment_with_status_integration(self):
        """Test réassignation de rendez-vous avec préservation du statut"""
        # Créer un utilisateur fantôme
        ghost_user = User(
            first_name='Ghost',
            last_name='User',
            email='deleted@system.local',
            password='Ghost#2025!',
            is_admin=False
        )
        self.save_to_db(ghost_user)
        
        # Créer un rendez-vous et le confirmer
        appointment = self.appointment_service.create_appointment(
            message="Reassignment test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        self.appointment_service.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        
        # Réassigner à l'utilisateur fantôme
        reassigned = self.appointment_service.reassign_appointments_from_user(
            self.user.id,
            ghost_user.id
        )
        
        self.assertEqual(len(reassigned), 1)
        
        # Vérifier que le statut est préservé
        updated_appointment = self.appointment_service.get_appointment_by_id(appointment.id)
        self.assertEqual(updated_appointment.status, AppointmentStatus.CONFIRMED)
        self.assertEqual(updated_appointment.user_id, ghost_user.id)

    def test_appointment_status_validation_integration(self):
        """Test validation des statuts dans le contexte d'intégration"""
        appointment = self.appointment_service.create_appointment(
            message="Validation test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Test avec tous les statuts valides
        valid_statuses = [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.COMPLETED
        ]
        
        for status in valid_statuses:
            updated = self.appointment_service.update_appointment_status(
                appointment.id,
                status=status
            )
            self.assertEqual(updated.status, status)
        
        # Test avec statut invalide
        with self.assertRaises(CustomError):
            self.appointment_service.update_appointment_status(
                appointment.id,
                status="invalid_status"
            )

    def test_appointment_search_by_status_integration(self):
        """Test recherche de rendez-vous par statut via les méthodes existantes"""
        # Créer plusieurs rendez-vous avec différents statuts
        appointments_data = [
            ("Pending appointment", AppointmentStatus.PENDING),
            ("Confirmed appointment", AppointmentStatus.CONFIRMED),
            ("Cancelled appointment", AppointmentStatus.CANCELLED),
            ("Completed appointment", AppointmentStatus.COMPLETED)
        ]
        
        created_appointments = []
        for message, status in appointments_data:
            appointment = self.appointment_service.create_appointment(
                message=message,
                user_id=self.user.id,
                prestation_id=self.prestation.id
            )
            
            if status != AppointmentStatus.PENDING:
                self.appointment_service.update_appointment_status(
                    appointment.id,
                    status=status
                )
            
            created_appointments.append(appointment)
        
        # Récupérer tous les rendez-vous de l'utilisateur
        user_appointments = self.appointment_service.get_appointment_by_user(self.user.id)
        self.assertEqual(len(user_appointments), 4)
        
        # Vérifier que tous les statuts sont présents
        statuses_found = [apt.status for apt in user_appointments]
        for _, expected_status in appointments_data:
            self.assertIn(expected_status, statuses_found)

    def test_appointment_prestation_relationship_with_status_integration(self):
        """Test relation rendez-vous/prestation avec gestion des statuts"""
        # Créer une deuxième prestation
        prestation2 = Prestation(name='Second Prestation')
        self.save_to_db(prestation2)
        
        # Créer des rendez-vous pour différentes prestations
        apt1 = self.appointment_service.create_appointment(
            message="First prestation appointment",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        apt2 = self.appointment_service.create_appointment(
            message="Second prestation appointment",
            user_id=self.user.id,
            prestation_id=prestation2.id
        )
        
        # Mettre à jour avec différents statuts
        self.appointment_service.update_appointment_status(
            apt1.id,
            status=AppointmentStatus.CONFIRMED
        )
        
        self.appointment_service.update_appointment_status(
            apt2.id,
            status=AppointmentStatus.CANCELLED
        )
        
        # Vérifier les rendez-vous par prestation
        prestation1_appointments = self.appointment_service.get_appointment_by_prestation(self.prestation.id)
        prestation2_appointments = self.appointment_service.get_appointment_by_prestation(prestation2.id)
        
        self.assertEqual(len(prestation1_appointments), 1)
        self.assertEqual(len(prestation2_appointments), 1)
        
        self.assertEqual(prestation1_appointments[0].status, AppointmentStatus.CONFIRMED)
        self.assertEqual(prestation2_appointments[0].status, AppointmentStatus.CANCELLED)

    def test_appointment_error_handling_integration(self):
        """Test gestion d'erreurs dans le contexte d'intégration"""
        appointment = self.appointment_service.create_appointment(
            message="Error handling test",
            user_id=self.user.id,
            prestation_id=self.prestation.id
        )
        
        # Test avec ID invalide
        with self.assertRaises(CustomError) as context:
            self.appointment_service.update_appointment_status(
                "invalid-id",
                status=AppointmentStatus.CONFIRMED
            )
        self.assertEqual(context.exception.status_code, 400)
        
        # Test avec rendez-vous inexistant
        with self.assertRaises(CustomError) as context:
            self.appointment_service.update_appointment_status(
                "12345678-1234-1234-1234-123456789012",
                status=AppointmentStatus.CONFIRMED
            )
        self.assertEqual(context.exception.status_code, 404)
        
        # Test avec statut invalide
        with self.assertRaises(CustomError) as context:
            self.appointment_service.update_appointment_status(
                appointment.id,
                status="invalid"
            )
        self.assertEqual(context.exception.status_code, 400)


if __name__ == '__main__':
    unittest.main()