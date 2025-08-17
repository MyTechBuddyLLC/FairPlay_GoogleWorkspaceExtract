import unittest
import copy

from src.masking import mask_user_profile

class TestMasking(unittest.TestCase):

    def setUp(self):
        """Set up mock user profiles for teacher and student."""
        self.teacher_profile = {
            'id': 'teacher123',
            'name': {'fullName': 'Alice Teacher'},
            'emailAddress': 'alice@example.com',
            'photoUrl': 'http://example.com/alice.jpg'
        }
        self.student_profile = {
            'id': 'student456',
            'name': {'fullName': 'Bob Student'},
            'emailAddress': 'bob@example.com',
            'photoUrl': 'http://example.com/bob.jpg'
        }

    def test_masking_level_none(self):
        """Tests that no masking occurs when level is 'none'."""
        original_teacher = copy.deepcopy(self.teacher_profile)
        original_student = copy.deepcopy(self.student_profile)

        masked_teacher = mask_user_profile(self.teacher_profile, 'TEACHER', 'none')
        masked_student = mask_user_profile(self.student_profile, 'STUDENT', 'none')

        self.assertEqual(masked_teacher, original_teacher)
        self.assertEqual(masked_student, original_student)

    def test_masking_level_students_only(self):
        """Tests that only students are masked when level is 'students_only'."""
        original_teacher = copy.deepcopy(self.teacher_profile)

        masked_teacher = mask_user_profile(self.teacher_profile, 'TEACHER', 'students_only')
        masked_student = mask_user_profile(self.student_profile, 'STUDENT', 'students_only')

        # Teacher should be unchanged
        self.assertEqual(masked_teacher, original_teacher)

        # Student should be masked
        self.assertEqual(masked_student['name']['fullName'], 'user_student456')
        self.assertEqual(masked_student['emailAddress'], 'user_student456@masked.local')
        self.assertEqual(masked_student['photoUrl'], '')

    def test_masking_level_all(self):
        """Tests that both students and teachers are masked when level is 'all'."""
        masked_teacher = mask_user_profile(self.teacher_profile, 'TEACHER', 'all')
        masked_student = mask_user_profile(self.student_profile, 'STUDENT', 'all')

        # Teacher should be masked
        self.assertEqual(masked_teacher['name']['fullName'], 'user_teacher123')
        self.assertEqual(masked_teacher['emailAddress'], 'user_teacher123@masked.local')
        self.assertEqual(masked_teacher['photoUrl'], '')

        # Student should be masked
        self.assertEqual(masked_student['name']['fullName'], 'user_student456')
        self.assertEqual(masked_student['emailAddress'], 'user_student456@masked.local')
        self.assertEqual(masked_student['photoUrl'], '')

if __name__ == '__main__':
    unittest.main()
