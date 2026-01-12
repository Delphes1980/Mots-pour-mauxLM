#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.models.prestation import Prestation


class TestAppointmentStatus(BaseTest):
    """Tests unitaires pour les statuts des rendez-vous"""
    
    def setUp(self):
        super().setUp()
        
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

    def test_appointment_status_constants(self):
        """Test que les constantes de statut sont correctement définies"""
        self.assertEqual(AppointmentStatus.PENDING, "PENDING")
        self.assertEqual(AppointmentStatus.CONFIRMED, "CONFIRMED")
        self.assertEqual(AppointmentStatus.CANCELLED, "CANCELLED")
        self.assertEqual(AppointmentStatus.COMPLETED, "COMPLETED")

    def test_appointment_default_status(self):
        """Test que le statut par défaut est PENDING"""
        appointment = Appointment(
            user=self.user,
            message="Test message",
            prestation=self.prestation
        )
        
        self.save_to_db(appointment)
        
        # Le statut par défaut devrait être PENDING après sauvegarde
        self.assertEqual(appointment.status, AppointmentStatus.PENDING)

    def test_appointment_valid_status_assignment(self):
        """Test assignation de statuts valides"""
        appointment = Appointment(
            user=self.user,
            message="Test message",
            prestation=self.prestation
        )
        
        valid_statuses = [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.COMPLETED
        ]
        
        for status in valid_statuses:
            appointment.status = status
            self.assertEqual(appointment.status, status)

    def test_appointment_invalid_status_assignment(self):
        """Test assignation de statuts invalides"""
        appointment = Appointment(
            user=self.user,
            message="Test message",
            prestation=self.prestation
        )
        
        invalid_statuses = [
            "invalid_status",
            "pending",  # Minuscules
            "pending_extra",
            "",
            None,
            123,
            []
        ]
        
        for invalid_status in invalid_statuses:
            with self.assertRaises(ValueError) as context:
                appointment.status = invalid_status
            
            self.assertIn("Invalid status", str(context.exception))

    def test_appointment_status_validation_message(self):
        """Test que le message d'erreur contient les statuts autorisés"""
        appointment = Appointment(
            user=self.user,
            message="Test message",
            prestation=self.prestation
        )
        
        with self.assertRaises(ValueError) as context:
            appointment.status = "invalid"
        
        error_message = str(context.exception)
        self.assertIn("PENDING", error_message)
        self.assertIn("CONFIRMED", error_message)
        self.assertIn("CANCELLED", error_message)
        self.assertIn("COMPLETED", error_message)

    def test_appointment_status_persistence(self):
        """Test que le statut est persisté en base de données"""
        appointment = Appointment(
            user=self.user,
            message="Test message",
            prestation=self.prestation
        )
        appointment.status = AppointmentStatus.CONFIRMED
        
        self.save_to_db(appointment)
        
        # Récupérer depuis la base
        retrieved_appointment = Appointment.query.filter_by(id=appointment.id).first()
        self.assertEqual(retrieved_appointment.status, AppointmentStatus.CONFIRMED)

    def test_appointment_status_update(self):
        """Test mise à jour du statut"""
        appointment = Appointment(
            user=self.user,
            message="Test message",
            prestation=self.prestation
        )
        
        self.save_to_db(appointment)
        
        # Changer le statut
        appointment.status = AppointmentStatus.COMPLETED
        self.db.session.commit()
        
        # Vérifier la mise à jour
        retrieved_appointment = Appointment.query.filter_by(id=appointment.id).first()
        self.assertEqual(retrieved_appointment.status, AppointmentStatus.COMPLETED)


if __name__ == '__main__':
    unittest.main()