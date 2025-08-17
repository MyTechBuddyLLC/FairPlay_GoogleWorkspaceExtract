"""
Handles loading and validation of the application configuration from a .ini file.
"""

import configparser
import os

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

def get_config(path: str = 'config.ini') -> configparser.ConfigParser:
    """
    Loads and validates the application configuration from the specified path.

    Args:
        path: The path to the configuration file (e.g., 'config.ini').

    Returns:
        A configparser object with the loaded configuration.

    Raises:
        ConfigError: If the configuration file is not found, is missing
                     required sections or keys, or if values are invalid.
    """
    if not os.path.exists(path):
        raise ConfigError(
            f"Configuration file not found at '{path}'. "
            f"Please copy 'config.ini.example' to '{path}' and fill in the values."
        )

    config = configparser.ConfigParser()
    config.read(path)

    # Validate required sections and keys
    required = {
        'GOOGLE': ['SERVICE_ACCOUNT_FILE', 'ADMIN_USER_EMAIL'],
        'DATABASE': ['PATH']
    }

    for section, keys in required.items():
        if section not in config:
            raise ConfigError(f"Missing required section '[{section}]' in '{path}'.")
        for key in keys:
            if key not in config[section] or not config[section][key]:
                raise ConfigError(
                    f"Missing or empty required key '{key}' in section '[{section}]' in '{path}'."
                )

    # Validate optional settings if they exist
    if 'SETTINGS' in config and 'PII_MASKING_LEVEL' in config['SETTINGS']:
        level = config['SETTINGS']['PII_MASKING_LEVEL'].lower()
        allowed_levels = ['none', 'students_only', 'all']
        if level not in allowed_levels:
            raise ConfigError(
                f"Invalid value for 'PII_MASKING_LEVEL'. Must be one of {allowed_levels}, but got '{level}'."
            )

    return config
