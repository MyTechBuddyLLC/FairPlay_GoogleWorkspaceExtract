import unittest
from unittest.mock import patch, mock_open
import configparser

from src.config import get_config, ConfigError

class TestConfig(unittest.TestCase):

    def test_get_config_success(self):
        """Tests successful loading of a valid config file."""
        mock_content = """
[GOOGLE]
SERVICE_ACCOUNT_FILE = path/to/creds.json
ADMIN_USER_EMAIL = admin@example.com
[DATABASE]
PATH = data.sqlite3
"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_content)):
                config = get_config('dummy_path.ini')
                self.assertIsInstance(config, configparser.ConfigParser)
                self.assertEqual(config.get('GOOGLE', 'SERVICE_ACCOUNT_FILE'), 'path/to/creds.json')
                self.assertEqual(config.get('DATABASE', 'PATH'), 'data.sqlite3')

    def test_get_config_file_not_found(self):
        """Tests that ConfigError is raised when the file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            with self.assertRaises(ConfigError) as cm:
                get_config('non_existent_path.ini')
            self.assertIn("Configuration file not found", str(cm.exception))

    def test_get_config_missing_section(self):
        """Tests that ConfigError is raised for a missing section."""
        mock_content = """
[GOOGLE]
SERVICE_ACCOUNT_FILE = path/to/creds.json
ADMIN_USER_EMAIL = admin@example.com
"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_content)):
                with self.assertRaises(ConfigError) as cm:
                    get_config('dummy_path.ini')
                self.assertIn("Missing required section '[DATABASE]'", str(cm.exception))

    def test_get_config_missing_key(self):
        """Tests that ConfigError is raised for a missing key in a section."""
        mock_content = """
[GOOGLE]
SERVICE_ACCOUNT_FILE = path/to/creds.json
[DATABASE]
PATH = data.sqlite3
"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_content)):
                with self.assertRaises(ConfigError) as cm:
                    get_config('dummy_path.ini')
                self.assertIn("Missing or empty required key 'ADMIN_USER_EMAIL'", str(cm.exception))

    def test_get_config_invalid_pii_level(self):
        """Tests that ConfigError is raised for an invalid PII_MASKING_LEVEL."""
        mock_content = """
[GOOGLE]
SERVICE_ACCOUNT_FILE = path/to/creds.json
ADMIN_USER_EMAIL = admin@example.com
[DATABASE]
PATH = data.sqlite3
[SETTINGS]
PII_MASKING_LEVEL = wrong_value
"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_content)):
                with self.assertRaises(ConfigError) as cm:
                    get_config('dummy_path.ini')
                self.assertIn("Invalid value for 'PII_MASKING_LEVEL'", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
