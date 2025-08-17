import unittest
from unittest.mock import patch, MagicMock
import configparser

from src.auth import get_classroom_service, SCOPES

class TestAuth(unittest.TestCase):

    def setUp(self):
        """Set up a mock config object for the tests."""
        self.mock_config = configparser.ConfigParser()
        self.mock_config['GOOGLE'] = {
            'SERVICE_ACCOUNT_FILE': 'fake_creds.json',
            'ADMIN_USER_EMAIL': 'admin@example.com'
        }

    @patch('src.auth.build')
    @patch('src.auth.google.oauth2.service_account.Credentials')
    def test_get_classroom_service(self, mock_credentials, mock_build):
        """
        Tests that the Google API service is built with the correct,
        delegated credentials.
        """
        # Arrange
        # Mock the credentials object and the delegated credentials object
        mock_creds_instance = MagicMock()
        mock_delegated_creds_instance = MagicMock()
        mock_credentials.from_service_account_file.return_value = mock_creds_instance
        mock_creds_instance.with_subject.return_value = mock_delegated_creds_instance

        # Mock the build object
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Act
        service = get_classroom_service(self.mock_config)

        # Assert
        # Check that credentials were loaded correctly
        mock_credentials.from_service_account_file.assert_called_once_with(
            'fake_creds.json', scopes=SCOPES
        )

        # Check that we impersonated the correct user
        mock_creds_instance.with_subject.assert_called_once_with('admin@example.com')

        # Check that the service was built with the delegated credentials
        mock_build.assert_called_once_with(
            'classroom', 'v1', credentials=mock_delegated_creds_instance
        )

        # Check that the final service object is returned
        self.assertEqual(service, mock_service)


if __name__ == '__main__':
    unittest.main()
