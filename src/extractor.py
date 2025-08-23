"""
Handles the extraction of data from the Google Classroom API.
"""

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

def get_courses(service: Resource) -> list:
    """
    Fetches all courses accessible by the authenticated user.

    Handles pagination to retrieve the complete list of courses.

    Args:
        service: An authorized Google Classroom API service resource object.

    Returns:
        A list of course objects.
    """
    courses = []
    page_token = None
    while True:
        try:
            response = service.courses().list(pageToken=page_token).execute()
            courses.extend(response.get('courses', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as e:
            print(f"An HTTP error occurred while fetching courses: {e}")
            break
    print(f"Found {len(courses)} courses.")
    return courses

def get_students(service: Resource, course_id: str) -> list:
    """
    Fetches all students enrolled in a specific course.

    Handles pagination to retrieve the complete list of students.

    Args:
        service: An authorized Google Classroom API service resource object.
        course_id: The ID of the course from which to fetch students.

    Returns:
        A list of student objects.
    """
    students = []
    page_token = None
    while True:
        try:
            response = service.courses().students().list(
                courseId=course_id, pageToken=page_token
            ).execute()
            students.extend(response.get('students', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as e:
            print(f"An HTTP error occurred while fetching students for course {course_id}: {e}")
            break
    return students

def get_teachers(service: Resource, course_id: str) -> list:
    """
    Fetches all teachers for a specific course.

    Handles pagination to retrieve the complete list of teachers.

    Args:
        service: An authorized Google Classroom API service resource object.
        course_id: The ID of the course from which to fetch teachers.

    Returns:
        A list of teacher objects.
    """
    teachers = []
    page_token = None
    while True:
        try:
            response = service.courses().teachers().list(
                courseId=course_id, pageToken=page_token
            ).execute()
            teachers.extend(response.get('teachers', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as e:
            print(f"An HTTP error occurred while fetching teachers for course {course_id}: {e}")
            break
    return teachers

def get_announcements(service: Resource, course_id: str) -> list:
    """
    Fetches all announcements for a specific course.

    Handles pagination to retrieve the complete list of announcements.

    Args:
        service: An authorized Google Classroom API service resource object.
        course_id: The ID of the course from which to fetch announcements.

    Returns:
        A list of announcement objects.
    """
    announcements = []
    page_token = None
    while True:
        try:
            response = service.courses().announcements().list(
                courseId=course_id, pageToken=page_token
            ).execute()
            announcements.extend(response.get('announcements', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as e:
            print(f"An HTTP error occurred while fetching announcements for course {course_id}: {e}")
            break
    return announcements

def get_course_work(service: Resource, course_id: str) -> list:
    """
    Fetches all course work (assignments, etc.) for a specific course.

    Args:
        service: An authorized Google Classroom API service resource object.
        course_id: The ID of the course from which to fetch course work.

    Returns:
        A list of course work objects.
    """
    course_work = []
    page_token = None
    while True:
        try:
            response = service.courses().courseWork().list(
                courseId=course_id, pageToken=page_token
            ).execute()
            course_work.extend(response.get('courseWork', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as e:
            print(f"An HTTP error occurred while fetching course work for course {course_id}: {e}")
            break
    return course_work

def get_student_submissions(service: Resource, course_id: str, course_work_id: str) -> list:
    """
    Fetches all student submissions for a specific piece of course work.

    Args:
        service: An authorized Google Classroom API service resource object.
        course_id: The ID of the course.
        course_work_id: The ID of the course work.

    Returns:
        A list of student submission objects.
    """
    submissions = []
    page_token = None
    while True:
        try:
            response = service.courses().courseWork().studentSubmissions().list(
                courseId=course_id,
                courseWorkId=course_work_id,
                pageToken=page_token
            ).execute()
            submissions.extend(response.get('studentSubmissions', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as e:
            print(f"An HTTP error occurred while fetching submissions for course work {course_work_id}: {e}")
            break
    return submissions
