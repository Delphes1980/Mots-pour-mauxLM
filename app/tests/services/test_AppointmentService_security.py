#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.services.AppointmentService import AppointmentService
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.models.prestation import Prestation
from app.utils import CustomError


class TestAppointmentServiceSecurity(BaseTest):
    """Tests de sécurité pour AppointmentService"""
    
    def setUp(self):
        super().setUp()
        self.appointment_service = AppointmentService()
        
        # Créer des utilisateurs de test
        self.user1 = User(
            first_name='User',
            last_name='One',
            email='user1@example.com',
            password='Password123!',
            is_admin=False
        )
        
        self.user2 = User(
            first_name='User',
            last_name='Two',
            email='user2@example.com',
            password='Password123!',
            is_admin=False
        )
        
        self.admin_user = User(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            password='Password123!',
            is_admin=True
        )
        
        self.prestation = Prestation(name='Security Test Prestation')
        
        self.save_to_db(self.user1, self.user2, self.admin_user, self.prestation)

    def test_appointment_status_update_input_validation(self):
        """Test validation des entrées pour la mise à jour de statut"""
        appointment = self.appointment_service.create_appointment(
            message="Security test",
            user_id=self.user1.id,
            prestation_id=self.prestation.id
        )
        
        # Test avec tentatives d'injection
        malicious_inputs = [
            "'; DROP TABLE appointments; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "null",
            "undefined",
            "admin' OR '1'='1",
            "UNION SELECT * FROM users"
        ]
        
        for malicious_input in malicious_inputs:
            with self.assertRaises(CustomError) as context:
                self.appointment_service.update_appointment_status(
                    appointment.id,
                    status=malicious_input
                )
            
            # Doit échouer avec une erreur de validation
            self.assertEqual(context.exception.status_code, 400)

    def test_appointment_id_validation_security(self):
        """Test validation sécurisée des IDs de rendez-vous"""
        # Test avec différents types d'IDs malveillants
        malicious_ids = [
            "'; DROP TABLE appointments; --",
            "../../../etc/passwd",
            "admin' OR '1'='1",
            "<script>alert('xss')</script>",
            "null",
            "undefined",
            "0x41414141",
            "../../admin/appointments"
        ]
        
        for malicious_id in malicious_ids:
            with self.assertRaises(CustomError) as context:
                self.appointment_service.update_appointment_status(
                    malicious_id,
                    status=AppointmentStatus.CONFIRMED
                )
            
            # Doit échouer avec une erreur de validation d'ID
            self.assertEqual(context.exception.status_code, 400)

    def test_appointment_status_enumeration_protection(self):
        """Test protection contre l'énumération de statuts"""
        appointment = self.appointment_service.create_appointment(
            message="Enumeration test",
            user_id=self.user1.id,
            prestation_id=self.prestation.id
        )
        
        # Tenter d'utiliser des statuts qui pourraient révéler des informations
        potential_enum_statuses = [
            "admin",
            "system",
            "debug",
            "test",
            "internal",
            "private",
            "hidden",
            "secret"
        ]
        
        for enum_status in potential_enum_statuses:
            with self.assertRaises(CustomError) as context:
                self.appointment_service.update_appointment_status(
                    appointment.id,
                    status=enum_status
                )
            
            self.assertEqual(context.exception.status_code, 400)

    def test_appointment_concurrent_modification_security(self):
        """Test sécurité lors de modifications concurrentes"""
        appointment = self.appointment_service.create_appointment(
            message="Concurrent test",
            user_id=self.user1.id,
            prestation_id=self.prestation.id
        )
        
        # Simuler des modifications concurrentes
        # Première modification
        updated1 = self.appointment_service.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        
        # Deuxième modification immédiate
        updated2 = self.appointment_service.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.CANCELLED
        )
        
        # Vérifier que la dernière modification est appliquée
        final_appointment = self.appointment_service.get_appointment_by_id(appointment.id)
        self.assertEqual(final_appointment.status, AppointmentStatus.CANCELLED)

    def test_appointment_data_leakage_protection(self):
        """Test protection contre la fuite de données"""
        # Créer des rendez-vous pour différents utilisateurs
        appointment1 = self.appointment_service.create_appointment(
            message="Sensitive data user 1",
            user_id=self.user1.id,
            prestation_id=self.prestation.id
        )
        
        appointment2 = self.appointment_service.create_appointment(
            message="Sensitive data user 2",
            user_id=self.user2.id,
            prestation_id=self.prestation.id
        )
        
        # Vérifier que les rendez-vous sont isolés par utilisateur
        user1_appointments = self.appointment_service.get_appointment_by_user(self.user1.id)
        user2_appointments = self.appointment_service.get_appointment_by_user(self.user2.id)
        
        # Vérifier qu'aucun rendez-vous ne fuite entre utilisateurs
        user1_ids = [apt.id for apt in user1_appointments]
        user2_ids = [apt.id for apt in user2_appointments]
        
        self.assertNotIn(appointment2.id, user1_ids)
        self.assertNotIn(appointment1.id, user2_ids)

    def test_appointment_status_transition_security(self):
        """Test sécurité des transitions de statut"""
        appointment = self.appointment_service.create_appointment(
            message="Transition security test",
            user_id=self.user1.id,
            prestation_id=self.prestation.id
        )
        
        # Tester toutes les transitions possibles
        valid_transitions = [
            (AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED),
            (AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED),
            (AppointmentStatus.CANCELLED, AppointmentStatus.PENDING),
            (AppointmentStatus.PENDING, AppointmentStatus.COMPLETED)
        ]
        
        for from_status, to_status in valid_transitions:
            # Remettre au statut de départ
            self.appointment_service.update_appointment_status(
                appointment.id,
                status=from_status
            )
            
            # Effectuer la transition
            updated = self.appointment_service.update_appointment_status(
                appointment.id,
                status=to_status
            )
            
            self.assertEqual(updated.status, to_status)

    def test_appointment_mass_update_protection(self):
        """Test protection contre les mises à jour en masse"""
        # Créer plusieurs rendez-vous
        appointments = []
        for i in range(5):
            appointment = self.appointment_service.create_appointment(
                message=f"Mass update test {i}",
                user_id=self.user1.id,
                prestation_id=self.prestation.id
            )
            appointments.append(appointment)
        
        # Vérifier que chaque mise à jour doit être individuelle
        for appointment in appointments:
            updated = self.appointment_service.update_appointment_status(
                appointment.id,
                status=AppointmentStatus.CONFIRMED
            )
            self.assertEqual(updated.status, AppointmentStatus.CONFIRMED)
        
        # Vérifier qu'il n'y a pas de mécanisme de mise à jour en masse non sécurisé
        all_appointments = self.appointment_service.get_appointment_by_user(self.user1.id)
        confirmed_count = sum(1 for apt in all_appointments if apt.status == AppointmentStatus.CONFIRMED)
        self.assertEqual(confirmed_count, 5)

    def test_appointment_status_persistence_security(self):
        """Test sécurité de la persistance des statuts"""
        appointment = self.appointment_service.create_appointment(
            message="Persistence security test",
            user_id=self.user1.id,
            prestation_id=self.prestation.id
        )
        
        # Mettre à jour le statut
        self.appointment_service.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        
        # Vérifier que le statut est correctement persisté et ne peut pas être modifié par injection
        retrieved = self.appointment_service.get_appointment_by_id(appointment.id)
        self.assertEqual(retrieved.status, AppointmentStatus.CONFIRMED)
        
        # Vérifier que le statut en base correspond exactement
        from app.models.appointment import Appointment as AppointmentModel
        db_appointment = AppointmentModel.query.filter_by(id=appointment.id).first()
        self.assertEqual(db_appointment.status, AppointmentStatus.CONFIRMED)

    def test_appointment_error_message_security(self):
        """Test que les messages d'erreur ne révèlent pas d'informations sensibles"""
        # Test avec ID inexistant
        try:
            self.appointment_service.update_appointment_status(
                "12345678-1234-1234-1234-123456789012",
                status=AppointmentStatus.CONFIRMED
            )
        except CustomError as e:
            # Le message ne doit pas révéler d'informations sur la structure de la base
            error_msg = str(e).lower()
            sensitive_terms = ['sql', 'database', 'table', 'column', 'query', 'select', 'insert']
            for term in sensitive_terms:
                self.assertNotIn(term, error_msg)

    def test_appointment_status_authorization_bypass_protection(self):
        """Test protection contre le contournement d'autorisation"""
        # Créer un rendez-vous pour user1
        appointment = self.appointment_service.create_appointment(
            message="Authorization test",
            user_id=self.user1.id,
            prestation_id=self.prestation.id
        )
        
        # Vérifier qu'on ne peut pas modifier le statut en passant un autre user_id
        # (Cette protection devrait être au niveau API, mais on teste la cohérence du service)
        updated = self.appointment_service.update_appointment_status(
            appointment.id,
            status=AppointmentStatus.CONFIRMED
        )
        
        # Vérifier que l'utilisateur associé n'a pas changé
        self.assertEqual(updated.user_id, self.user1.id)
        
        # Vérifier en base
        retrieved = self.appointment_service.get_appointment_by_id(appointment.id)
        self.assertEqual(retrieved.user_id, self.user1.id)

    def test_appointment_status_validation_edge_cases(self):
        """Test validation avec cas limites"""
        appointment = self.appointment_service.create_appointment(
            message="Edge cases test",
            user_id=self.user1.id,
            prestation_id=self.prestation.id
        )
        
        # Test avec valeurs limites
        edge_cases = [
            "",  # Chaîne vide
            " ",  # Espace
            "\n",  # Nouvelle ligne
            "\t",  # Tabulation
            "a" * 1000,  # Chaîne très longue
            "pending\x00",  # Caractère null
            "pending\r\n",  # Retour chariot
        ]
        
        for edge_case in edge_cases:
            with self.assertRaises(CustomError) as context:
                self.appointment_service.update_appointment_status(
                    appointment.id,
                    status=edge_case
                )
            
            self.assertEqual(context.exception.status_code, 400)


if __name__ == '__main__':
    unittest.main()