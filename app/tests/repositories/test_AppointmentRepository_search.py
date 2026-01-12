#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment, AppointmentStatus
from app.persistence.AppointmentRepository import AppointmentRepository


class TestAppointmentRepositorySearch(BaseTest):
    """Tests pour la recherche de rendez-vous par statut - Repository"""

    def setUp(self):
        super().setUp()
        self.repository = AppointmentRepository()
        
        # Créer utilisateurs et prestation
        self.user = User(
            first_name='User',
            last_name='Test',
            email='user@test.com',
            password='Password123!',
            is_admin=False
        )
        
        self.prestation = Prestation(name='Test Prestation')
        self.save_to_db(self.user, self.prestation)

    def test_get_appointments_by_status_pending(self):
        """Test récupération des rendez-vous par statut PENDING"""
        appointment1 = Appointment(user=self.user, message="RDV pending 1", prestation=self.prestation)
        appointment1.status = AppointmentStatus.PENDING
        
        appointment2 = Appointment(user=self.user, message="RDV confirmed", prestation=self.prestation)
        appointment2.status = AppointmentStatus.CONFIRMED
        
        appointment3 = Appointment(user=self.user, message="RDV pending 2", prestation=self.prestation)
        appointment3.status = AppointmentStatus.PENDING
        
        self.save_to_db(appointment1, appointment2, appointment3)
        
        result = self.repository.get_appointments_by_status(AppointmentStatus.PENDING)
        
        self.assertEqual(len(result), 2)
        for appointment in result:
            self.assertEqual(appointment.status, AppointmentStatus.PENDING)

    def test_get_appointments_by_status_confirmed(self):
        """Test récupération des rendez-vous par statut CONFIRMED"""
        appointment = Appointment(user=self.user, message="RDV confirmed", prestation=self.prestation)
        appointment.status = AppointmentStatus.CONFIRMED
        self.save_to_db(appointment)
        
        result = self.repository.get_appointments_by_status(AppointmentStatus.CONFIRMED)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, AppointmentStatus.CONFIRMED)
        self.assertEqual(result[0].message, "RDV confirmed")

    def test_get_appointments_by_status_cancelled(self):
        """Test récupération des rendez-vous par statut CANCELLED"""
        appointment = Appointment(user=self.user, message="RDV cancelled", prestation=self.prestation)
        appointment.status = AppointmentStatus.CANCELLED
        self.save_to_db(appointment)
        
        result = self.repository.get_appointments_by_status(AppointmentStatus.CANCELLED)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, AppointmentStatus.CANCELLED)

    def test_get_appointments_by_status_completed(self):
        """Test récupération des rendez-vous par statut COMPLETED"""
        appointment = Appointment(user=self.user, message="RDV completed", prestation=self.prestation)
        appointment.status = AppointmentStatus.COMPLETED
        self.save_to_db(appointment)
        
        result = self.repository.get_appointments_by_status(AppointmentStatus.COMPLETED)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, AppointmentStatus.COMPLETED)

    def test_get_appointments_by_status_no_results(self):
        """Test recherche sans résultats"""
        # Créer un rendez-vous avec un statut différent
        appointment = Appointment(user=self.user, message="RDV pending", prestation=self.prestation)
        appointment.status = AppointmentStatus.PENDING
        self.save_to_db(appointment)
        
        result = self.repository.get_appointments_by_status(AppointmentStatus.COMPLETED)
        
        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)

    def test_get_appointments_by_status_multiple_users(self):
        """Test recherche avec plusieurs utilisateurs"""
        user2 = User(
            first_name='UserTwo',
            last_name='Test',
            email='user2@test.com',
            password='Password123!',
            is_admin=False
        )
        self.save_to_db(user2)
        
        # Créer des rendez-vous pour différents utilisateurs avec le même statut
        appointment1 = Appointment(user=self.user, message="RDV user1", prestation=self.prestation)
        appointment1.status = AppointmentStatus.PENDING
        
        appointment2 = Appointment(user=user2, message="RDV user2", prestation=self.prestation)
        appointment2.status = AppointmentStatus.PENDING
        
        self.save_to_db(appointment1, appointment2)
        
        result = self.repository.get_appointments_by_status(AppointmentStatus.PENDING)
        
        self.assertEqual(len(result), 2)
        user_ids = [appointment.user_id for appointment in result]
        self.assertIn(self.user.id, user_ids)
        self.assertIn(user2.id, user_ids)

    def test_get_appointments_by_status_multiple_prestations(self):
        """Test recherche avec plusieurs prestations"""
        prestation2 = Prestation(name='Test Prestation 2')
        self.save_to_db(prestation2)
        
        # Créer des rendez-vous pour différentes prestations avec le même statut
        appointment1 = Appointment(user=self.user, message="RDV prestation1", prestation=self.prestation)
        appointment1.status = AppointmentStatus.CONFIRMED
        
        appointment2 = Appointment(user=self.user, message="RDV prestation2", prestation=prestation2)
        appointment2.status = AppointmentStatus.CONFIRMED
        
        self.save_to_db(appointment1, appointment2)
        
        result = self.repository.get_appointments_by_status(AppointmentStatus.CONFIRMED)
        
        self.assertEqual(len(result), 2)
        prestation_ids = [appointment.prestation_id for appointment in result]
        self.assertIn(self.prestation.id, prestation_ids)
        self.assertIn(prestation2.id, prestation_ids)

    def test_get_appointments_by_status_all_statuses(self):
        """Test recherche pour tous les statuts possibles"""
        statuses = [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.COMPLETED
        ]
        
        # Créer un rendez-vous pour chaque statut
        for i, status in enumerate(statuses):
            appointment = Appointment(user=self.user, message=f"RDV {status}", prestation=self.prestation)
            appointment.status = status
            self.save_to_db(appointment)
        
        # Vérifier chaque statut
        for status in statuses:
            result = self.repository.get_appointments_by_status(status)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].status, status)


if __name__ == '__main__':
    unittest.main()