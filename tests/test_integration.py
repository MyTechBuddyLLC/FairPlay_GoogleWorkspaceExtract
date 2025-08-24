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

    def setUp(self):
        """A helper to create mock data for reuse."""
        self.mock_course = {'id': 'course1', 'name': 'Test Course', 'section': '101', 'description': 'Desc', 'courseState': 'ACTIVE', 'creationTime': 't1', 'updateTime': 't2'}
        self.mock_teacher = {'profile': {'id': 'teacher1', 'name': {'fullName': 'Prof Test'}, 'emailAddress': 'prof@test.com', 'photoUrl': ''}}
        self.mock_student = {'profile': {'id': 'student1', 'name': {'fullName': 'Stud Test'}, 'emailAddress': 'stud@test.com', 'photoUrl': ''}}
        self.mock_announcement = {'id': 'anno1', 'courseId': 'course1', 'creatorUserId': 'teacher1', 'text': 'Hello', 'state': 'PUBLISHED', 'creationTime': 't3', 'updateTime': 't4'}
        self.mock_work = {'id': 'work1', 'courseId': 'course1', 'title': 'Test Assignment', 'maxPoints': 100, 'creationTime': 't5', 'updateTime': 't6', 'creatorUserId': 'teacher1'}
        self.mock_submission = {'id': 'sub1', 'courseWorkId': 'work1', 'userId': 'student1', 'state': 'TURNED_IN', 'assignedGrade': 95, 'creationTime': 't7', 'updateTime': 't8'}

    @patch('main.get_config')
    @patch('main.get_classroom_service')
    def test_end_to_end_flow(self, mock_get_service, mock_get_config):
        """Tests the full application flow with the new schema."""
        # --- Arrange ---
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key, fallback=None: ':memory:' if key == 'PATH' else 'none'
        mock_get_config.return_value = mock_config

        conn = initialize_database(':memory:')
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_service.courses().list().execute.return_value = {'courses': [self.mock_course]}
        mock_service.courses().teachers().list().execute.return_value = {'teachers': [self.mock_teacher]}
        mock_service.courses().students().list().execute.return_value = {'students': [self.mock_student]}
        mock_service.courses().announcements().list().execute.return_value = {'announcements': [self.mock_announcement]}
        mock_service.courses().courseWork().list().execute.return_value = {'courseWork': [self.mock_work]}
        mock_service.courses().courseWork().studentSubmissions().list().execute.return_value = {'studentSubmissions': [self.mock_submission]}

        # --- Act ---
        main.main(db_conn_for_testing=conn)

        # --- Assert ---
        cursor = conn.cursor()

        # Verify data in tables
        cursor.execute("SELECT NM FROM CRSS WHERE ID='course1'")
        self.assertEqual(cursor.fetchone()[0], 'Test Course')
        cursor.execute("SELECT NM FROM USRS WHERE ID='teacher1'")
        self.assertEqual(cursor.fetchone()[0], 'Prof Test')

        # Verify data in views
        cursor.execute("SELECT USR_NM FROM VW_ENRLLMNT_DTLS WHERE CRS_NM='Test Course' AND USR_RL='STUDENT'")
        self.assertEqual(cursor.fetchone()[0], 'Stud Test')
        cursor.execute("SELECT ASSGND_GRD FROM VW_ASSGNMNT_GRDS WHERE STNDT_NM='Stud Test'")
        self.assertEqual(cursor.fetchone()[0], 95)
        
        conn.close()

    @patch('main.get_config')
    @patch('main.get_classroom_service')
    def test_end_to_end_flow_with_student_masking(self, mock_get_service, mock_get_config):
        """Tests the full application flow with student PII masking enabled and new schema."""
        # --- Arrange ---
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key, fallback=None: ':memory:' if key == 'PATH' else 'students_only'
        mock_get_config.return_value = mock_config

        conn = initialize_database(':memory:')
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_service.courses().list().execute.return_value = {'courses': [self.mock_course]}
        mock_service.courses().teachers().list().execute.return_value = {'teachers': [self.mock_teacher]}
        mock_service.courses().students().list().execute.return_value = {'students': [self.mock_student]}
        mock_service.courses().announcements().list().execute.return_value = {}
        mock_service.courses().courseWork().list().execute.return_value = {}

        # --- Act ---
        main.main(db_conn_for_testing=conn)

        # --- Assert ---
        cursor = conn.cursor()

        # Verify teacher data is NOT masked
        cursor.execute("SELECT NM, EML FROM USRS WHERE ID='teacher1'")
        self.assertEqual(cursor.fetchone(), ('Prof Test', 'prof@test.com'))

        # Verify student data IS masked
        cursor.execute("SELECT NM, EML FROM USRS WHERE ID='student1'")
        self.assertEqual(cursor.fetchone(), ('user_student1', 'user_student1@masked.local'))

        conn.close()

if __name__ == '__main__':
    unittest.main()
