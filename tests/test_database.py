import unittest
import sqlite3

from src.database import (
    initialize_database, save_user, save_course, save_enrollment,
    save_announcement, save_course_work, save_student_submission
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
        """Tests that all tables are created upon initialization."""
        tables = [
            'users', 'courses', 'enrollments', 'announcements',
            'course_work', 'student_submissions'
        ]
        for table in tables:
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            self.assertIsNotNone(self.cursor.fetchone(), f"Table '{table}' was not created.")

    def test_save_user(self):
        """Tests saving a user and the ON CONFLICT DO UPDATE behavior."""
        user_profile = {
            'id': 'user123',
            'name': {'fullName': 'Test User'},
            'emailAddress': 'test@example.com',
            'photoUrl': 'http://example.com/photo.jpg'
        }
        save_user(self.conn, user_profile)
        self.conn.commit()

        # Verify insertion
        self.cursor.execute("SELECT * FROM users WHERE id='user123';")
        user_row = self.cursor.fetchone()
        self.assertEqual(user_row, ('user123', 'Test User', 'test@example.com', 'http://example.com/photo.jpg'))

        # Test update
        user_profile['name']['fullName'] = 'Test User Updated'
        save_user(self.conn, user_profile)
        self.conn.commit()
        self.cursor.execute("SELECT name FROM users WHERE id='user123';")
        self.assertEqual(self.cursor.fetchone()[0], 'Test User Updated')

    def test_save_course(self):
        """Tests saving a course."""
        course_data = {
            'id': 'course456', 'name': 'Test Course', 'section': 'TC101',
            'description': 'A test course.', 'creationTime': '2024-01-01T00:00:00Z',
            'updateTime': '2024-01-01T00:00:00Z', 'courseState': 'ACTIVE'
        }
        save_course(self.conn, course_data)
        self.conn.commit()
        self.cursor.execute("SELECT name, section FROM courses WHERE id='course456';")
        self.assertEqual(self.cursor.fetchone(), ('Test Course', 'TC101'))

    def test_save_enrollment(self):
        """Tests saving an enrollment and the ON CONFLICT DO NOTHING behavior."""
        # Need to insert user and course first due to foreign key constraints
        self.test_save_user()
        self.test_save_course()

        save_enrollment(self.conn, 'course456', 'user123', 'STUDENT')
        self.conn.commit()
        self.cursor.execute("SELECT role FROM enrollments WHERE course_id='course456' AND user_id='user123';")
        self.assertEqual(self.cursor.fetchone()[0], 'STUDENT')

        # Try to insert again, should do nothing
        save_enrollment(self.conn, 'course456', 'user123', 'STUDENT')
        self.conn.commit()
        self.cursor.execute("SELECT COUNT(*) FROM enrollments;")
        self.assertEqual(self.cursor.fetchone()[0], 1)


if __name__ == '__main__':
    unittest.main()
