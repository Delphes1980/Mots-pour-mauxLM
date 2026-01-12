#!/usr/bin/env python3

import unittest
from app.tests.base_test import BaseTest
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment
from app.services.AppointmentService import AppointmentService
from app.utils import CustomError


class TestAppointmentServiceDelete(BaseTest):
    """Tests pour la suppression de rendez-vous - Service"""

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

    def test_delete_appointment_success(self):
        """Test suppression réussie d'un rendez-vous"""
        appointment = Appointment(user=self.user, message="Test delete", prestation=self.prestation)
        self.save_to_db(appointment)
        
        result = self.service.delete_appointment(str(appointment.id))
        
        self.assertTrue(result)
        
        # Vérifier que le rendez-vous a été supprimé
        # Forcer une nouvelle requête après expire_all()
        from app import db
        db.session.close()
        deleted_appointment = Appointment.query.get(appointment.id)
        self.assertIsNone(deleted_appointment)

    def test_delete_appointment_not_found(self):
        """Test suppression d'un rendez-vous inexistant"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        
        with self.assertRaises(CustomError) as context:
            self.service.delete_appointment(fake_id)
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn('Rendez-vous non trouvé', str(context.exception))

    def test_delete_appointment_invalid_id(self):
        """Test suppression avec ID invalide"""
        invalid_ids = ['invalid-id', '12345', 'not-a-uuid', '']
        
        for invalid_id in invalid_ids:
            with self.assertRaises(CustomError) as context:
                self.service.delete_appointment(invalid_id)
            
            self.assertEqual(context.exception.status_code, 400)


if __name__ == '__main__':
    unittest.main()