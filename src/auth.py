"""
Handles Google API authentication and service creation.
"""

from configparser import ConfigParser
import google.oauth2.service_account
from googleapiclient.discovery import build, Resource

# Define the scopes required for the application. These are all read-only.
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.students.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly',
    'https://www.googleapis.com/auth/classroom.announcements.readonly',
    'https://www.googleapis.com/auth/classroom.profile.emails',
    'https://www.googleapis.com/auth/classroom.profile.photos',
]

def get_classroom_service(config: ConfigParser) -> Resource:
    """
    Creates and returns an authenticated Google Classroom API service object.

    This function uses a service account to authenticate and impersonates a
    Google Workspace admin user to gain domain-wide access to Classroom data.

    Args:
        config: A ConfigParser object containing the application configuration,
                including the service account file path and the admin user's email.

    Returns:
        An authorized Google Classroom API service resource object.

    Raises:
        FileNotFoundError: If the service account credentials file is not found.
        Exception: For other potential errors during authentication.
    """
    service_account_file = config.get('GOOGLE', 'SERVICE_ACCOUNT_FILE')
    admin_user_email = config.get('GOOGLE', 'ADMIN_USER_EMAIL')

    creds = google.oauth2.service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )

    # Impersonate the admin user to get domain-wide access
    delegated_creds = creds.with_subject(admin_user_email)

    try:
        service = build('classroom', 'v1', credentials=delegated_creds)
        return service
    except Exception as e:
        print(f"An error occurred while building the Google Classroom service: {e}")
        print(
            "Please ensure the Google Classroom API is enabled in your Google Cloud project "
            "and that the service account has the necessary permissions."
        )
        raise
