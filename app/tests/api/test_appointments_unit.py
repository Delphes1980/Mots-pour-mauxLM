import json
import unittest
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token

# Assurez-vous d'importer la BaseTest appropriée pour l'initialisation de la DB de test
from app.tests.base_test import BaseTest
# Importation des modèles pour interagir directement avec eux
from app.models.user import User
from app.models.prestation import Prestation
from app.models.appointment import Appointment
# Aucune importation de l'API nécessaire pour les tests de modèle purs


class TestAppointmentModel(BaseTest):
    """
    Tests unitaires du modèle Appointment, vérifiant la création,
    les relations et les méthodes de sérialisation, en utilisant
    directement la DB de test sans passer par l'API HTTP.
    (Note : Ce fichier est renommé d'après le chemin de l'erreur pour le débogage, 
    mais contient des tests de MODÈLE).
    """

    def setUp(self):
        """
        Initialisation de la base de test et création des dépendances (Users, Prestations).
        """
        super().setUp()

        # Créer utilisateurs pour les clés étrangères
        self.regular_user = User(
            email='user@test.com',
            password='Password123!',
            first_name='User',
            last_name='Test',
            is_admin=False
        )
        self.other_user = User(
            email='other@test.com',
            password='Password123!',
            first_name='Other',
            last_name='User',
            is_admin=False
        )
        self.save_to_db(self.regular_user, self.other_user)

        # Créer prestations pour les clés étrangères
        self.prestation1 = Prestation(name='Massage')
        self.prestation2 = Prestation(name='Acupuncture')
        self.save_to_db(self.prestation1, self.prestation2)


    # --- Tests de Création et d'Attributs ---

    def test_appointment_model_creation(self):
        """Vérifie la création d'une instance d'Appointment avec les bonnes relations."""
        message = 'Rendez-vous test pour vérification unitaire.'

        appointment = Appointment(
            message=message,
            user=self.regular_user,
            prestation=self.prestation1
        )
        self.save_to_db(appointment)

        # Vérification des attributs
        self.assertEqual(appointment.message, message)
        self.assertEqual(appointment.user_id, self.regular_user.id)
        self.assertEqual(appointment.prestation_id, self.prestation1.id)
        self.assertIsInstance(appointment.created_at, datetime)
        self.assertIsInstance(appointment.updated_at, datetime)

        # Vérification des relations (accès aux objets via les propriétés ORM)
        self.assertEqual(appointment.user.first_name, 'User')
        self.assertEqual(appointment.prestation.name, 'Massage')

    # --- Test des Propriétés Directes (Remplace le test to_dict) ---

    def test_appointment_properties_format(self):
        """
        Vérifie que les propriétés de l'objet Appointment sont correctement
        chargées/liées, sans utiliser de méthode de sérialisation to_dict().
        """
        appointment = Appointment(
            message='Vérification des propriétés',
            user=self.regular_user,
            prestation=self.prestation2
        )
        self.save_to_db(appointment)

        # Vérification des propriétés directes de l'objet ORM
        self.assertIsNotNone(appointment.id)
        self.assertEqual(appointment.message, 'Vérification des propriétés')
        self.assertEqual(appointment.user_id, self.regular_user.id)
        self.assertEqual(appointment.prestation_id, self.prestation2.id)
        
        # Vérification des relations ORM (accès aux objets liés)
        self.assertIsNotNone(appointment.user)
        self.assertEqual(appointment.user.first_name, 'User')
        self.assertIsNotNone(appointment.prestation)
        self.assertEqual(appointment.prestation.name, 'Acupuncture')


    # --- Tests de Requêtes (Querying) ---

    def test_appointments_query_by_user(self):
        """Vérifie que la DB récupère correctement les RDVs pour un utilisateur donné."""
        # RDVs pour regular_user
        app1 = Appointment(message='R1', user=self.regular_user, prestation=self.prestation1)
        app2 = Appointment(message='R2', user=self.regular_user, prestation=self.prestation2)
        # RDVs pour other_user
        app3 = Appointment(message='O3', user=self.other_user, prestation=self.prestation1)

        self.save_to_db(app1, app2, app3)

        # Vérification pour l'utilisateur régulier
        user_appointments = Appointment.query.filter_by(user_id=self.regular_user.id).all()
        self.assertEqual(len(user_appointments), 2)
        self.assertTrue(all(a.user_id == self.regular_user.id for a in user_appointments))

        # Vérification pour l'autre utilisateur
        other_appointments = Appointment.query.filter_by(user_id=self.other_user.id).all()
        self.assertEqual(len(other_appointments), 1)

        # Vérification pour un utilisateur sans RDV
        fake_user_appointments = Appointment.query.filter_by(user_id=str(self.prestation1.id)).all()
        self.assertEqual(len(fake_user_appointments), 0)


    def test_appointments_query_by_prestation(self):
        """Vérifie que la DB récupère correctement les RDVs pour une prestation donnée."""
        # RDVs pour Massage (prestation1)
        app1 = Appointment(message='R1', user=self.regular_user, prestation=self.prestation1)
        app3 = Appointment(message='O3', user=self.other_user, prestation=self.prestation1)
        # RDV pour Acupuncture (prestation2)
        app2 = Appointment(message='R2', user=self.regular_user, prestation=self.prestation2)

        self.save_to_db(app1, app2, app3)

        # Vérification pour prestation1 (Massage)
        massage_appointments = Appointment.query.filter_by(prestation_id=self.prestation1.id).all()
        self.assertEqual(len(massage_appointments), 2)
        self.assertTrue(all(a.prestation_id == self.prestation1.id for a in massage_appointments))

        # Vérification pour prestation2 (Acupuncture)
        acupuncture_appointments = Appointment.query.filter_by(prestation_id=self.prestation2.id).all()
        self.assertEqual(len(acupuncture_appointments), 1)

if __name__ == '__main__':
    unittest.main()
