#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.services.AppointmentService import AppointmentService
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.models.prestation import Prestation
from app.utils import CustomError


class TestAppointmentServiceStatusUpdate(BaseTest):
    """Tests unitaires pour la mise à jour du statut des rendez-vous"""
    
    def setUp(self):
        super().setUp()
        self.appointment_service = AppointmentService()
        
        # Créer des objets de test
        self.user = User(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='Password123!',
            is_admin=False
        )
        
        self.prestation = Prestation(name='Test Prestation')
        
        self.save_to_db(self.user, self.prestation)
        
        # Créer un rendez-vous de test directement
        self.appointment = Appointment(
            message="Test appointment message",
            user=self.user,
            prestation=self.prestation
        )
        self.save_to_db(self.appointment)

    def test_update_appointment_status_success(self):
        """Test mise à jour réussie du statut"""
        updated_appointment = self.appointment_service.update_appointment_status(
            self.appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        
        self.assertEqual(updated_appointment.status, AppointmentStatus.CONFIRMED)
        self.assertEqual(updated_appointment.id, self.appointment.id)

    def test_update_appointment_status_all_valid_statuses(self):
        """Test mise à jour avec tous les statuts valides"""
        valid_statuses = [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.COMPLETED,
            AppointmentStatus.PENDING
        ]
        
        for status in valid_statuses:
            updated_appointment = self.appointment_service.update_appointment_status(
                self.appointment.id,
                status=status
            )
            self.assertEqual(updated_appointment.status, status)

    def test_update_appointment_status_invalid_appointment_id(self):
        """Test avec ID de rendez-vous invalide"""
        invalid_ids = [
            "invalid-id",
            "",
            None,
            "12345678-1234-1234-1234-123456789012"  # UUID valide mais inexistant
        ]
        
        for invalid_id in invalid_ids:
            with self.assertRaises(CustomError) as context:
                self.appointment_service.update_appointment_status(
                    invalid_id,
                    status=AppointmentStatus.CONFIRMED
                )
            
            if invalid_id == "12345678-1234-1234-1234-123456789012":
                self.assertEqual(context.exception.status_code, 404)
            else:
                self.assertEqual(context.exception.status_code, 400)

    def test_update_appointment_status_invalid_status(self):
        """Test avec statut invalide"""
        invalid_statuses = [
            "invalid_status",
            "confirmed",  # Minuscules
            "",
            None,
            123,
            []
        ]
        
        for invalid_status in invalid_statuses:
            with self.assertRaises(CustomError) as context:
                self.appointment_service.update_appointment_status(
                    self.appointment.id,
                    status=invalid_status
                )
            
            self.assertEqual(context.exception.status_code, 400)

    def test_update_appointment_status_missing_status(self):
        """Test sans fournir de statut"""
        with self.assertRaises(CustomError) as context:
            self.appointment_service.update_appointment_status(
                self.appointment.id
            )
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("status", str(context.exception))

    def test_update_appointment_status_nonexistent_appointment(self):
        """Test avec rendez-vous inexistant"""
        nonexistent_id = "12345678-1234-1234-1234-123456789012"
        
        with self.assertRaises(CustomError) as context:
            self.appointment_service.update_appointment_status(
                nonexistent_id,
                status=AppointmentStatus.CONFIRMED
            )
        
        self.assertEqual(context.exception.status_code, 404)

    def test_update_appointment_status_persistence(self):
        """Test que la mise à jour est persistée en base"""
        # Mettre à jour le statut
        self.appointment_service.update_appointment_status(
            self.appointment.id,
            status=AppointmentStatus.COMPLETED
        )
        
        # Récupérer depuis la base pour vérifier
        self.db.session.refresh(self.appointment)
        self.assertEqual(self.appointment.status, AppointmentStatus.COMPLETED)

    def test_update_appointment_status_multiple_updates(self):
        """Test mises à jour multiples du même rendez-vous"""
        statuses_sequence = [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.PENDING,
            AppointmentStatus.COMPLETED
        ]
        
        for status in statuses_sequence:
            updated_appointment = self.appointment_service.update_appointment_status(
                self.appointment.id,
                status=status
            )
            self.assertEqual(updated_appointment.status, status)
            
            # Vérifier en base
            self.db.session.refresh(self.appointment)
            self.assertEqual(self.appointment.status, status)

    def test_update_appointment_status_with_deleted_user(self):
        """Test mise à jour du statut avec utilisateur supprimé"""
        # Créer un utilisateur fantôme
        ghost_user = User(
            first_name='Ghost',
            last_name='User',
            email='deleted@system.local',
            password='Ghost#2025!',
            is_admin=False
        )
        self.save_to_db(ghost_user)
        
        # Réassigner le rendez-vous à l'utilisateur fantôme
        self.appointment.user = ghost_user
        self.db.session.commit()
        
        # La mise à jour du statut devrait toujours fonctionner
        updated_appointment = self.appointment_service.update_appointment_status(
            self.appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        
        self.assertEqual(updated_appointment.status, AppointmentStatus.CONFIRMED)

    def test_update_appointment_status_validation_order(self):
        """Test que les validations sont effectuées dans le bon ordre"""
        # ID invalide devrait être vérifié en premier
        with self.assertRaises(CustomError) as context:
            self.appointment_service.update_appointment_status(
                "invalid-id",
                status="invalid-status"
            )
        
        # Devrait échouer sur l'ID, pas sur le statut
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("appointment_id", str(context.exception))


if __name__ == '__main__':
    unittest.main()