import unittest
from unittest.mock import MagicMock

from src.extractor import (
    get_courses, get_students, get_teachers, get_announcements,
    get_course_work, get_student_submissions
)

class TestExtractor(unittest.TestCase):

    def setUp(self):
        """Set up a mock service object for each test."""
        self.mock_service = MagicMock()

    def test_get_courses_pagination(self):
        """Tests that get_courses correctly handles API pagination."""
        # Mock the API response for two pages of results
        self.mock_service.courses().list().execute.side_effect = [
            {'courses': [{'id': 'course1'}], 'nextPageToken': 'token123'},
            {'courses': [{'id': 'course2'}]}
        ]

        courses = get_courses(self.mock_service)

        self.assertEqual(len(courses), 2)
        self.assertEqual(courses[0]['id'], 'course1')
        self.assertEqual(courses[1]['id'], 'course2')
        # Ensure the mock was called twice (once for each page)
        self.assertEqual(self.mock_service.courses().list().execute.call_count, 2)

    def test_get_students(self):
        """Tests fetching students for a course."""
        self.mock_service.courses().students().list().execute.return_value = {
            'students': [{'userId': 'student1'}]
        }
        students = get_students(self.mock_service, 'course1')
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0]['userId'], 'student1')
        self.mock_service.courses().students().list.assert_called_with(
            courseId='course1', pageToken=None
        )

    def test_get_teachers(self):
        """Tests fetching teachers for a course."""
        self.mock_service.courses().teachers().list().execute.return_value = {
            'teachers': [{'userId': 'teacher1'}]
        }
        teachers = get_teachers(self.mock_service, 'course1')
        self.assertEqual(len(teachers), 1)
        self.assertEqual(teachers[0]['userId'], 'teacher1')

    def test_get_announcements(self):
        """Tests fetching announcements for a course."""
        self.mock_service.courses().announcements().list().execute.return_value = {
            'announcements': [{'id': 'anno1'}]
        }
        announcements = get_announcements(self.mock_service, 'course1')
        self.assertEqual(len(announcements), 1)
        self.assertEqual(announcements[0]['id'], 'anno1')

    def test_get_course_work(self):
        """Tests fetching course work for a course."""
        self.mock_service.courses().courseWork().list().execute.return_value = {
            'courseWork': [{'id': 'cw1'}]
        }
        course_work = get_course_work(self.mock_service, 'course1')
        self.assertEqual(len(course_work), 1)
        self.assertEqual(course_work[0]['id'], 'cw1')

    def test_get_student_submissions(self):
        """Tests fetching submissions for a course work item."""
        self.mock_service.courses().courseWork().studentSubmissions().list().execute.return_value = {
            'studentSubmissions': [{'id': 'sub1'}]
        }
        submissions = get_student_submissions(self.mock_service, 'course1', 'cw1')
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0]['id'], 'sub1')
        self.mock_service.courses().courseWork().studentSubmissions().list.assert_called_with(
            courseId='course1', courseWorkId='cw1', pageToken=None
        )

if __name__ == '__main__':
    unittest.main()
