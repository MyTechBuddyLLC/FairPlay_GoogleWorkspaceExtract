import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import os

# Add parent directory to path to import main
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main
from src.database import initialize_database

class TestIntegration(unittest.TestCase):

    @patch('main.get_config')
    @patch('main.get_classroom_service')
    def test_end_to_end_flow(self, mock_get_service, mock_get_config):
        """
        Tests the full application flow from config loading to data persistence,
        using a mocked Google API service and an in-memory database.
        """
        # 1. --- Arrange ---

        # Mock configuration. It's still needed for the auth part.
        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        # Set up an in-memory database for the test
        conn = initialize_database(':memory:')

        # Mock the Google API Service and its responses
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Define mock API data
        mock_course = {'id': 'course1', 'name': 'Test Course', 'section': '101', 'description': 'Desc', 'courseState': 'ACTIVE', 'creationTime': 't1', 'updateTime': 't2'}
        mock_teacher = {'profile': {'id': 'teacher1', 'name': {'fullName': 'Prof Test'}, 'emailAddress': 'prof@test.com', 'photoUrl': ''}}
        mock_student = {'profile': {'id': 'student1', 'name': {'fullName': 'Stud Test'}, 'emailAddress': 'stud@test.com', 'photoUrl': ''}}
        mock_announcement = {'id': 'anno1', 'courseId': 'course1', 'creatorUserId': 'teacher1', 'text': 'Hello', 'state': 'PUBLISHED', 'creationTime': 't3', 'updateTime': 't4'}
        mock_work = {'id': 'work1', 'courseId': 'course1', 'title': 'Test Assignment', 'maxPoints': 100, 'creationTime': 't5', 'updateTime': 't6'}
        mock_submission = {'id': 'sub1', 'courseWorkId': 'work1', 'userId': 'student1', 'state': 'TURNED_IN', 'assignedGrade': 95, 'creationTime': 't7', 'updateTime': 't8'}

        # Configure the mock service's return values
        mock_service.courses().list().execute.return_value = {'courses': [mock_course]}
        mock_service.courses().teachers().list().execute.return_value = {'teachers': [mock_teacher]}
        mock_service.courses().students().list().execute.return_value = {'students': [mock_student]}
        mock_service.courses().announcements().list().execute.return_value = {'announcements': [mock_announcement]}
        mock_service.courses().courseWork().list().execute.return_value = {'courseWork': [mock_work]}
        mock_service.courses().courseWork().studentSubmissions().list().execute.return_value = {'studentSubmissions': [mock_submission]}

        # 2. --- Act ---
        # Run the main application function, injecting the test database connection
        main.main(db_conn_for_testing=conn)

        # 3. --- Assert ---
        cursor = conn.cursor()

        # Verify course data
        cursor.execute("SELECT name FROM courses WHERE id='course1'")
        self.assertEqual(cursor.fetchone()[0], 'Test Course')

        # Verify user data (teacher and student)
        cursor.execute("SELECT name FROM users WHERE id='teacher1'")
        self.assertEqual(cursor.fetchone()[0], 'Prof Test')
        cursor.execute("SELECT name FROM users WHERE id='student1'")
        self.assertEqual(cursor.fetchone()[0], 'Stud Test')

        # Verify enrollment data
        cursor.execute("SELECT role FROM enrollments WHERE course_id='course1' AND user_id='student1'")
        self.assertEqual(cursor.fetchone()[0], 'STUDENT')

        # Verify announcement data
        cursor.execute("SELECT text FROM announcements WHERE id='anno1'")
        self.assertEqual(cursor.fetchone()[0], 'Hello')

        # Verify course work data
        cursor.execute("SELECT title FROM course_work WHERE id='work1'")
        self.assertEqual(cursor.fetchone()[0], 'Test Assignment')

        # Verify submission data
        cursor.execute("SELECT assigned_grade FROM student_submissions WHERE id='sub1'")
        self.assertEqual(cursor.fetchone()[0], 95)

        # Clean up
        conn.close()

    @patch('main.get_config')
    @patch('main.get_classroom_service')
    def test_end_to_end_flow_with_student_masking(self, mock_get_service, mock_get_config):
        """
        Tests the full application flow with student PII masking enabled.
        """
        # --- Arrange ---
        mock_config = MagicMock()
        # Set the masking level for this test case
        mock_config.get.side_effect = lambda section, key, fallback=None: ':memory:' if key == 'PATH' else 'students_only'
        mock_get_config.return_value = mock_config

        conn = initialize_database(':memory:')
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_course = {'id': 'course1', 'name': 'Test Course', 'section': '101', 'description': 'Desc', 'courseState': 'ACTIVE', 'creationTime': 't1', 'updateTime': 't2'}
        mock_teacher = {'profile': {'id': 'teacher1', 'name': {'fullName': 'Prof Test'}, 'emailAddress': 'prof@test.com', 'photoUrl': ''}}
        mock_student = {'profile': {'id': 'student1', 'name': {'fullName': 'Stud Test'}, 'emailAddress': 'stud@test.com', 'photoUrl': ''}}

        mock_service.courses().list().execute.return_value = {'courses': [mock_course]}
        mock_service.courses().teachers().list().execute.return_value = {'teachers': [mock_teacher]}
        mock_service.courses().students().list().execute.return_value = {'students': [mock_student]}
        # Make other API calls return empty lists to simplify the test
        mock_service.courses().announcements().list().execute.return_value = {}
        mock_service.courses().courseWork().list().execute.return_value = {}

        # --- Act ---
        main.main(db_conn_for_testing=conn)

        # --- Assert ---
        cursor = conn.cursor()

        # Verify teacher data is NOT masked
        cursor.execute("SELECT name, email FROM users WHERE id='teacher1'")
        teacher_row = cursor.fetchone()
        self.assertEqual(teacher_row, ('Prof Test', 'prof@test.com'))

        # Verify student data IS masked
        cursor.execute("SELECT name, email FROM users WHERE id='student1'")
        student_row = cursor.fetchone()
        self.assertEqual(student_row, ('user_student1', 'user_student1@masked.local'))

        conn.close()


if __name__ == '__main__':
    unittest.main()
