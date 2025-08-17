"""
Manages the SQLite database, including connection, schema creation, and data persistence.
"""

import sqlite3
from sqlite3 import Connection

def initialize_database(db_path: str) -> Connection:
    """
    Initializes the SQLite database.

    Connects to the database file, enables foreign key support, and creates the
    necessary tables if they do not already exist.

    Args:
        db_path: The file path for the SQLite database.

    Returns:
        An active sqlite3.Connection object to the database.
    """
    try:
        conn = sqlite3.connect(db_path)
        # Enable foreign key constraint enforcement
        conn.execute("PRAGMA foreign_keys = ON;")

        cursor = conn.cursor()

        # Create tables based on a 3NF schema
        # Users table (stores all unique users, both teachers and students)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            photo_url TEXT
        );
        """)

        # Courses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            section TEXT,
            description TEXT,
            creation_time TEXT,
            update_time TEXT,
            course_state TEXT
        );
        """)

        # Enrollments table (junction table for many-to-many relationship between users and courses)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('TEACHER', 'STUDENT')),
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(course_id, user_id)
        );
        """)

        # Announcements table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id TEXT PRIMARY KEY,
            course_id TEXT NOT NULL,
            creator_user_id TEXT NOT NULL,
            text TEXT,
            state TEXT,
            creation_time TEXT,
            update_time TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            FOREIGN KEY (creator_user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # Course Work table (assignments, questions, etc.)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_work (
            id TEXT PRIMARY KEY,
            course_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            work_type TEXT,
            max_points REAL,
            creation_time TEXT,
            update_time TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
        """)

        # Student Submissions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_submissions (
            id TEXT PRIMARY KEY,
            course_work_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            state TEXT,
            assigned_grade REAL,
            draft_grade REAL,
            creation_time TEXT,
            update_time TEXT,
            FOREIGN KEY (course_work_id) REFERENCES course_work(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        conn.commit()
        print(f"Database initialized successfully at '{db_path}'.")
        return conn
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise

def save_user(conn: Connection, user_profile: dict):
    """Saves a single user's profile to the database."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (id, name, email, photo_url)
        VALUES (:userId, :name, :emailAddress, :photoUrl)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            email=excluded.email,
            photo_url=excluded.photo_url;
    """, {
        'userId': user_profile['id'],
        'name': user_profile['name']['fullName'],
        'emailAddress': user_profile['emailAddress'],
        'photoUrl': user_profile.get('photoUrl')
    })

def save_course(conn: Connection, course: dict):
    """Saves a single course to the database."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO courses (id, name, section, description, creation_time, update_time, course_state)
        VALUES (:id, :name, :section, :description, :creationTime, :updateTime, :courseState)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            section=excluded.section,
            description=excluded.description,
            update_time=excluded.update_time,
            course_state=excluded.course_state;
    """, {
        'id': course['id'],
        'name': course['name'],
        'section': course.get('section'),
        'description': course.get('description'),
        'creationTime': course['creationTime'],
        'updateTime': course['updateTime'],
        'courseState': course['courseState']
    })

def save_enrollment(conn: Connection, course_id: str, user_id: str, role: str):
    """Saves a single enrollment record to the database."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO enrollments (course_id, user_id, role)
        VALUES (?, ?, ?)
        ON CONFLICT(course_id, user_id) DO NOTHING;
    """, (course_id, user_id, role))

def save_announcement(conn: Connection, announcement: dict):
    """Saves a single announcement to the database."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO announcements (id, course_id, creator_user_id, text, state, creation_time, update_time)
        VALUES (:id, :courseId, :creatorUserId, :text, :state, :creationTime, :updateTime)
        ON CONFLICT(id) DO UPDATE SET
            text=excluded.text,
            state=excluded.state,
            update_time=excluded.update_time;
    """, {
        'id': announcement['id'],
        'courseId': announcement['courseId'],
        'creatorUserId': announcement['creatorUserId'],
        'text': announcement.get('text'),
        'state': announcement.get('state'),
        'creationTime': announcement['creationTime'],
        'updateTime': announcement['updateTime']
    })

def save_course_work(conn: Connection, course_work_item: dict):
    """Saves a single course work item to the database."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO course_work (id, course_id, title, description, work_type, max_points, creation_time, update_time)
        VALUES (:id, :courseId, :title, :description, :workType, :maxPoints, :creationTime, :updateTime)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            description=excluded.description,
            work_type=excluded.work_type,
            max_points=excluded.max_points,
            update_time=excluded.update_time;
    """, {
        'id': course_work_item['id'],
        'courseId': course_work_item['courseId'],
        'title': course_work_item.get('title'),
        'description': course_work_item.get('description'),
        'workType': course_work_item.get('workType'),
        'maxPoints': course_work_item.get('maxPoints'),
        'creationTime': course_work_item['creationTime'],
        'updateTime': course_work_item['updateTime']
    })

def save_student_submission(conn: Connection, submission: dict):
    """Saves a single student submission to the database."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO student_submissions (id, course_work_id, user_id, state, assigned_grade, draft_grade, creation_time, update_time)
        VALUES (:id, :courseWorkId, :userId, :state, :assignedGrade, :draftGrade, :creationTime, :updateTime)
        ON CONFLICT(id) DO UPDATE SET
            state=excluded.state,
            assigned_grade=excluded.assigned_grade,
            draft_grade=excluded.draft_grade,
            update_time=excluded.update_time;
    """, {
        'id': submission['id'],
        'courseWorkId': submission['courseWorkId'],
        'userId': submission['userId'],
        'state': submission.get('state'),
        'assignedGrade': submission.get('assignedGrade'),
        'draftGrade': submission.get('draftGrade'),
        'creationTime': submission['creationTime'],
        'updateTime': submission['updateTime']
    })
