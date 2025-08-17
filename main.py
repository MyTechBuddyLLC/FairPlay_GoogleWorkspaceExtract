"""
FairPlay Google Workspace Extract
=================================
This application extracts data from Google Classroom and stores it in a
local SQLite database.
"""

import sys
from sqlite3 import Connection

from src.config import get_config, ConfigError
from src.auth import get_classroom_service
from src.database import (
    initialize_database, save_course, save_user, save_enrollment,
    save_announcement, save_course_work, save_student_submission
)
from src.extractor import (
    get_courses, get_teachers, get_students, get_announcements,
    get_course_work, get_student_submissions
)
from src.masking import mask_user_profile

def main(db_conn_for_testing: Connection = None):
    """
    Main function to run the data extraction process.

    Args:
        db_conn_for_testing: An optional database connection object.
                             If provided, it will be used for the operations.
                             If None, a new connection will be created based on config.
                             This is primarily for testing purposes.
    """
    print("Starting FairPlay Google Workspace Extract...")

    conn = None  # Ensure conn is defined in the outer scope
    try:
        # If a connection is provided for testing, use it. Otherwise, create one.
        if db_conn_for_testing:
            conn = db_conn_for_testing
        else:
            # 1. Load Configuration
            print("Loading configuration...")
            config = get_config()
            db_path = config.get('DATABASE', 'PATH')

            # 2. Initialize Database
            print(f"Initializing database at '{db_path}'...")
            conn = initialize_database(db_path)

        # Load configuration
        config = get_config()
        masking_level = config.get('SETTINGS', 'PII_MASKING_LEVEL', fallback='none').lower()

        # 3. Authenticate and get Google Classroom Service
        print("Authenticating with Google Workspace...")
        service = get_classroom_service(config)

        # 4. Extract and Save Data
        print("Fetching courses...")
        courses = get_courses(service)

        if not courses:
            print("No courses found or user does not have permission to view them.")
            return

        for course in courses:
            print(f"\nProcessing course: {course['name']} ({course['id']})")
            save_course(conn, course)

            # Process teachers
            print(f"  Fetching teachers for {course['name']}...")
            teachers = get_teachers(service, course['id'])
            for teacher in teachers:
                # Mask PII if required, then save
                masked_profile = mask_user_profile(teacher['profile'], 'TEACHER', masking_level)
                save_user(conn, masked_profile)
                save_enrollment(conn, course['id'], masked_profile['id'], 'TEACHER')
            print(f"  Found and processed {len(teachers)} teachers.")

            # Process students
            print(f"  Fetching students for {course['name']}...")
            students = get_students(service, course['id'])
            for student in students:
                # Some student profiles might be incomplete if they have been deleted
                if 'name' in student['profile'] and 'emailAddress' in student['profile']:
                    # Mask PII if required, then save
                    masked_profile = mask_user_profile(student['profile'], 'STUDENT', masking_level)
                    save_user(conn, masked_profile)
                    save_enrollment(conn, course['id'], masked_profile['id'], 'STUDENT')
                else:
                    print(f"  Skipping student with incomplete profile: {student['profile'].get('id')}")
            print(f"  Found and processed {len(students)} students.")

            # Process announcements
            print(f"  Fetching announcements for {course['name']}...")
            announcements = get_announcements(service, course['id'])
            for announcement in announcements:
                save_announcement(conn, announcement)
            print(f"  Found and processed {len(announcements)} announcements.")

            # Process course work and submissions
            print(f"  Fetching course work for {course['name']}...")
            course_works = get_course_work(service, course['id'])
            for work_item in course_works:
                save_course_work(conn, work_item)
                print(f"    Processing submissions for assignment: {work_item.get('title')} ({work_item['id']})")
                submissions = get_student_submissions(service, course['id'], work_item['id'])
                for submission in submissions:
                    save_student_submission(conn, submission)
            print(f"  Found and processed {len(course_works)} course work items and their submissions.")

            conn.commit() # Commit after each course is fully processed

        print("\nData extraction process completed successfully.")

    except ConfigError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Only close the connection if it was created by this function
        if db_conn_for_testing is None and 'conn' in locals() and isinstance(conn, Connection):
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
