import unittest
from unittest.mock import Mock, patch
from app.services.facade import Facade


class TestFacade(unittest.TestCase):
    """Tests pour la classe Facade"""

    def setUp(self):
        self.facade = Facade()
        
        # Mock tous les services
        self.facade.user_service = Mock()
        self.facade.review_service = Mock()
        self.facade.appointment_service = Mock()
        self.facade.prestation_service = Mock()
        self.facade.authentication_service = Mock()

    # Tests User operations
    def test_create_user(self):
        """Test délégation create_user"""
        mock_user = Mock()
        self.facade.user_service.create_user.return_value = mock_user
        
        result = self.facade.create_user(first_name="John", last_name="Doe")
        
        self.assertEqual(result, mock_user)
        self.facade.user_service.create_user.assert_called_once_with(first_name="John", last_name="Doe")

    def test_get_user_by_id(self):
        """Test délégation get_user_by_id"""
        mock_user = Mock()
        self.facade.user_service.get_user_by_id.return_value = mock_user
        
        result = self.facade.get_user_by_id("user-id")
        
        self.assertEqual(result, mock_user)
        self.facade.user_service.get_user_by_id.assert_called_once_with("user-id")

    def test_update_user(self):
        """Test délégation update_user"""
        mock_user = Mock()
        self.facade.user_service.update_user.return_value = mock_user
        
        result = self.facade.update_user("user-id", first_name="Jane")
        
        self.assertEqual(result, mock_user)
        self.facade.user_service.update_user.assert_called_once_with("user-id", first_name="Jane")

    def test_delete_user(self):
        """Test délégation delete_user"""
        self.facade.user_service.delete_user.return_value = True
        
        result = self.facade.delete_user("user-id")
        
        self.assertTrue(result)
        self.facade.user_service.delete_user.assert_called_once_with("user-id")

    # Tests Authentication operations
    def test_login(self):
        """Test délégation login"""
        mock_user = Mock()
        self.facade.authentication_service.login.return_value = mock_user
        
        result = self.facade.login("test@example.com", "password")
        
        self.assertEqual(result, mock_user)
        self.facade.authentication_service.login.assert_called_once_with("test@example.com", "password")

    def test_change_password(self):
        """Test délégation change_password"""
        mock_user = Mock()
        self.facade.authentication_service.change_password.return_value = mock_user
        
        result = self.facade.change_password("user-id", "old", "new")
        
        self.assertEqual(result, mock_user)
        self.facade.authentication_service.change_password.assert_called_once_with("user-id", "old", "new")

    # Tests Review operations
    def test_create_review(self):
        """Test délégation create_review"""
        mock_review = Mock()
        self.facade.review_service.create_review.return_value = mock_review
        
        result = self.facade.create_review(rating=5, text="Great")
        
        self.assertEqual(result, mock_review)
        self.facade.review_service.create_review.assert_called_once_with(rating=5, text="Great")

    def test_get_review_by_prestation(self):
        """Test délégation get_review_by_prestation"""
        mock_reviews = [Mock(), Mock()]
        self.facade.review_service.get_review_by_prestation.return_value = mock_reviews
        
        result = self.facade.get_review_by_prestation("prestation-id")
        
        self.assertEqual(result, mock_reviews)
        self.facade.review_service.get_review_by_prestation.assert_called_once_with("prestation-id")

    # Tests Appointment operations
    def test_create_appointment(self):
        """Test délégation create_appointment"""
        mock_appointment = Mock()
        self.facade.appointment_service.create_appointment.return_value = mock_appointment
        
        result = self.facade.create_appointment(message="Test", user_id="user-id")
        
        self.assertEqual(result, mock_appointment)
        self.facade.appointment_service.create_appointment.assert_called_once_with(message="Test", user_id="user-id")

    def test_get_appointment_by_user_and_prestation(self):
        """Test délégation get_appointment_by_user_and_prestation"""
        mock_appointments = [Mock()]
        self.facade.appointment_service.get_appointment_by_user_and_prestation.return_value = mock_appointments
        
        result = self.facade.get_appointment_by_user_and_prestation("user-id", "prestation-id")
        
        self.assertEqual(result, mock_appointments)
        self.facade.appointment_service.get_appointment_by_user_and_prestation.assert_called_once_with("user-id", "prestation-id")

    # Tests Prestation operations
    def test_create_prestation(self):
        """Test délégation create_prestation"""
        mock_prestation = Mock()
        self.facade.prestation_service.create_prestation.return_value = mock_prestation
        
        result = self.facade.create_prestation(name="Massage")
        
        self.assertEqual(result, mock_prestation)
        self.facade.prestation_service.create_prestation.assert_called_once_with(name="Massage")

    def test_get_prestation_by_name(self):
        """Test délégation get_prestation_by_name"""
        mock_prestation = Mock()
        self.facade.prestation_service.get_prestation_by_name.return_value = mock_prestation
        
        result = self.facade.get_prestation_by_name("Massage")
        
        self.assertEqual(result, mock_prestation)
        self.facade.prestation_service.get_prestation_by_name.assert_called_once_with("Massage")

    def test_facade_initialization(self):
        """Test que la façade initialise tous les services"""
        new_facade = Facade()
        
        self.assertIsNotNone(new_facade.user_service)
        self.assertIsNotNone(new_facade.review_service)
        self.assertIsNotNone(new_facade.appointment_service)
        self.assertIsNotNone(new_facade.prestation_service)
        self.assertIsNotNone(new_facade.authentication_service)


if __name__ == '__main__':
    unittest.main()