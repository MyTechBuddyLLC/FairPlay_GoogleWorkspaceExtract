import unittest
import sqlite3

from src.database import (
    initialize_database, create_views, save_user, save_course,
    save_enrollment, save_announcement, save_course_work, save_student_submission
)

class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory SQLite database for each test."""
        self.conn = initialize_database(':memory:')
        self.cursor = self.conn.cursor()

    def tearDown(self):
        """Close the database connection after each test."""
        self.conn.close()

    def test_initialize_database(self):
        """Tests that all tables are created upon initialization with correct names."""
        tables = ['USRS', 'CRSS', 'ENRLLMNTS', 'ANNCMNTS', 'CRS_WRK', 'STDNT_SBMSSNS']
        for table in tables:
            with self.subTest(table=table):
                self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
                self.assertIsNotNone(self.cursor.fetchone(), f"Table '{table}' was not created.")

    def _populate_data_for_views(self):
        """Helper function to populate DB with data needed for view tests."""
        # Save a user, course, and enrollment
        user_profile = {'id': 'user123', 'name': {'fullName': 'Test User'}, 'emailAddress': 'test@example.com', 'photoUrl': ''}
        course_data = {'id': 'course456', 'name': 'Test Course', 'section': 'TC101', 'description': 'A test course.', 'creationTime': 't1', 'updateTime': 't2', 'courseState': 'ACTIVE'}
        save_user(self.conn, user_profile)
        save_course(self.conn, course_data)
        save_enrollment(self.conn, 'course456', 'user123', 'STUDENT')

        # Save an announcement
        announcement_data = {'id': 'anno1', 'courseId': 'course456', 'creatorUserId': 'user123', 'text': 'Hello', 'state': 'PUBLISHED', 'creationTime': 't3', 'updateTime': 't4'}
        save_announcement(self.conn, announcement_data)

        # Save course work and a submission
        course_work_data = {'id': 'cw1', 'courseId': 'course456', 'title': 'Test Assignment', 'creationTime': 't5', 'updateTime': 't6'}
        submission_data = {'id': 'sub1', 'courseWorkId': 'cw1', 'userId': 'user123', 'state': 'RETURNED', 'assignedGrade': None, 'creationTime': 't7', 'updateTime': 't8'}
        save_course_work(self.conn, course_work_data)
        save_student_submission(self.conn, submission_data)
        self.conn.commit()

    def test_create_views(self):
        """Tests that all views are created and contain expected data."""
        self._populate_data_for_views()
        create_views(self.conn)

        views = ['VW_ENRLLMNT_DTLS', 'VW_ASSGNMNT_GRDS', 'VW_CRS_ACTVTY_LG', 'VW_SIS_ENRLLMNT_ROSTER']
        for view in views:
            with self.subTest(view=view):
                self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='view' AND name='{view}';")
                self.assertIsNotNone(self.cursor.fetchone(), f"View '{view}' was not created.")

        # Test the excused logic in the assignment grades view
        self.cursor.execute("SELECT SBMSSN_STS FROM VW_ASSGNMNT_GRDS WHERE STNDT_NM='Test User'")
        self.assertEqual(self.cursor.fetchone()[0], 'EXCSD')

    def test_save_user(self):
        """Tests saving a user with new naming conventions."""
        user_profile = {'id': 'user123', 'name': {'fullName': 'Test User'}, 'emailAddress': 'test@example.com', 'photoUrl': 'http://example.com/photo.jpg'}
        save_user(self.conn, user_profile)
        self.conn.commit()
        self.cursor.execute("SELECT * FROM USRS WHERE ID='user123';")
        self.assertEqual(self.cursor.fetchone(), ('user123', 'Test User', 'test@example.com', 'http://example.com/photo.jpg'))

    def test_save_course(self):
        """Tests saving a course with new naming conventions."""
        course_data = {'id': 'course456', 'name': 'Test Course', 'section': 'TC101', 'description': 'A test course.', 'creationTime': 't1', 'updateTime': 't2', 'courseState': 'ACTIVE'}
        save_course(self.conn, course_data)
        self.conn.commit()
        self.cursor.execute("SELECT NM, SCTN FROM CRSS WHERE ID='course456';")
        self.assertEqual(self.cursor.fetchone(), ('Test Course', 'TC101'))

    def test_save_enrollment(self):
        """Tests saving an enrollment with new naming conventions."""
        self.test_save_user()
        self.test_save_course()
        save_enrollment(self.conn, 'course456', 'user123', 'STUDENT')
        self.conn.commit()
        self.cursor.execute("SELECT RL FROM ENRLLMNTS WHERE CRS_ID='course456' AND USR_ID='user123';")
        self.assertEqual(self.cursor.fetchone()[0], 'STUDENT')

if __name__ == '__main__':
    unittest.main()
