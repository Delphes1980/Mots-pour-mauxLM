#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment, AppointmentStatus
from app.services.AppointmentService import AppointmentService
from app.utils import CustomError


class TestAppointmentServiceSearch(BaseTest):
    """Tests pour la recherche de rendez-vous par statut - Service"""

    def setUp(self):
        super().setUp()
        self.service = AppointmentService()
        
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
        
        result = self.service.get_appointments_by_status(AppointmentStatus.PENDING)
        
        self.assertEqual(len(result), 2)
        for appointment in result:
            self.assertEqual(appointment.status, AppointmentStatus.PENDING)

    def test_get_appointments_by_status_confirmed(self):
        """Test récupération des rendez-vous par statut CONFIRMED"""
        appointment = Appointment(user=self.user, message="RDV confirmed", prestation=self.prestation)
        appointment.status = AppointmentStatus.CONFIRMED
        self.save_to_db(appointment)
        
        result = self.service.get_appointments_by_status(AppointmentStatus.CONFIRMED)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, AppointmentStatus.CONFIRMED)
        self.assertEqual(result[0].message, "RDV confirmed")

    def test_get_appointments_by_status_cancelled(self):
        """Test récupération des rendez-vous par statut CANCELLED"""
        appointment = Appointment(user=self.user, message="RDV cancelled", prestation=self.prestation)
        appointment.status = AppointmentStatus.CANCELLED
        self.save_to_db(appointment)
        
        result = self.service.get_appointments_by_status(AppointmentStatus.CANCELLED)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, AppointmentStatus.CANCELLED)

    def test_get_appointments_by_status_completed(self):
        """Test récupération des rendez-vous par statut COMPLETED"""
        appointment = Appointment(user=self.user, message="RDV completed", prestation=self.prestation)
        appointment.status = AppointmentStatus.COMPLETED
        self.save_to_db(appointment)
        
        result = self.service.get_appointments_by_status(AppointmentStatus.COMPLETED)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, AppointmentStatus.COMPLETED)

    def test_get_appointments_by_status_empty_status(self):
        """Test avec statut vide"""
        with self.assertRaises(CustomError) as context:
            self.service.get_appointments_by_status("")
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn('requis', str(context.exception))

    def test_get_appointments_by_status_none_status(self):
        """Test avec statut None"""
        with self.assertRaises(CustomError) as context:
            self.service.get_appointments_by_status(None)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn('requis', str(context.exception))

    def test_get_appointments_by_status_invalid_status(self):
        """Test avec statut invalide"""
        with self.assertRaises(CustomError) as context:
            self.service.get_appointments_by_status("INVALID_STATUS")
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn('invalide', str(context.exception))

    def test_get_appointments_by_status_no_results(self):
        """Test recherche sans résultats"""
        # Créer un rendez-vous avec un statut différent
        appointment = Appointment(user=self.user, message="RDV pending", prestation=self.prestation)
        appointment.status = AppointmentStatus.PENDING
        self.save_to_db(appointment)
        
        with self.assertRaises(CustomError) as context:
            self.service.get_appointments_by_status(AppointmentStatus.COMPLETED)
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn('Aucun rendez-vous trouvé', str(context.exception))

    def test_get_appointments_by_status_multiple_statuses(self):
        """Test avec plusieurs rendez-vous de statuts différents"""
        appointments_data = [
            (AppointmentStatus.PENDING, "RDV pending 1"),
            (AppointmentStatus.PENDING, "RDV pending 2"),
            (AppointmentStatus.CONFIRMED, "RDV confirmed"),
            (AppointmentStatus.CANCELLED, "RDV cancelled"),
            (AppointmentStatus.COMPLETED, "RDV completed"),
        ]
        
        for status, message in appointments_data:
            appointment = Appointment(user=self.user, message=message, prestation=self.prestation)
            appointment.status = status
            self.save_to_db(appointment)
        
        # Test chaque statut
        pending_results = self.service.get_appointments_by_status(AppointmentStatus.PENDING)
        self.assertEqual(len(pending_results), 2)
        
        confirmed_results = self.service.get_appointments_by_status(AppointmentStatus.CONFIRMED)
        self.assertEqual(len(confirmed_results), 1)
        
        cancelled_results = self.service.get_appointments_by_status(AppointmentStatus.CANCELLED)
        self.assertEqual(len(cancelled_results), 1)
        
        completed_results = self.service.get_appointments_by_status(AppointmentStatus.COMPLETED)
        self.assertEqual(len(completed_results), 1)


if __name__ == '__main__':
    unittest.main()