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
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS USRS (
            ID TEXT PRIMARY KEY,
            NM TEXT NOT NULL,
            EML TEXT NOT NULL UNIQUE,
            PHT_URL TEXT
        );
        """)

        # Courses table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CRSS (
            ID TEXT PRIMARY KEY,
            NM TEXT NOT NULL,
            SCTN TEXT,
            DSCRPTN TEXT,
            CRTN_TM TEXT,
            UPDT_TM TEXT,
            CRS_STT TEXT
        );
        """)

        # Enrollments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ENRLLMNTS (
            ENRLLMNT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CRS_ID TEXT NOT NULL,
            USR_ID TEXT NOT NULL,
            RL TEXT NOT NULL CHECK(RL IN ('TEACHER', 'STUDENT')),
            FOREIGN KEY (CRS_ID) REFERENCES CRSS(ID) ON DELETE CASCADE,
            FOREIGN KEY (USR_ID) REFERENCES USRS(ID) ON DELETE CASCADE,
            UNIQUE(CRS_ID, USR_ID)
        );
        """)

        # Announcements table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ANNCMNTS (
            ID TEXT PRIMARY KEY,
            CRS_ID TEXT NOT NULL,
            CRTR_USR_ID TEXT NOT NULL,
            TXT TEXT,
            STT TEXT,
            CRTN_TM TEXT,
            UPDT_TM TEXT,
            FOREIGN KEY (CRS_ID) REFERENCES CRSS(ID) ON DELETE CASCADE,
            FOREIGN KEY (CRTR_USR_ID) REFERENCES USRS(ID) ON DELETE CASCADE
        );
        """)

        # Course Work table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CRS_WRK (
            ID TEXT PRIMARY KEY,
            CRS_ID TEXT NOT NULL,
            TTL TEXT NOT NULL,
            DSCRPTN TEXT,
            WRK_TYP TEXT,
            MX_PNTS REAL,
            CRTN_TM TEXT,
            UPDT_TM TEXT,
            FOREIGN KEY (CRS_ID) REFERENCES CRSS(ID) ON DELETE CASCADE
        );
        """)

        # Student Submissions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS STDNT_SBMSSNS (
            ID TEXT PRIMARY KEY,
            CRS_WRK_ID TEXT NOT NULL,
            USR_ID TEXT NOT NULL,
            STT TEXT,
            ASSGND_GRD REAL,
            DRFT_GRD REAL,
            CRTN_TM TEXT,
            UPDT_TM TEXT,
            FOREIGN KEY (CRS_WRK_ID) REFERENCES CRS_WRK(ID) ON DELETE CASCADE,
            FOREIGN KEY (USR_ID) REFERENCES USRS(ID) ON DELETE CASCADE
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
        INSERT INTO USRS (ID, NM, EML, PHT_URL)
        VALUES (:userId, :name, :emailAddress, :photoUrl)
        ON CONFLICT(ID) DO UPDATE SET
            NM=excluded.NM,
            EML=excluded.EML,
            PHT_URL=excluded.PHT_URL;
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
        INSERT INTO CRSS (ID, NM, SCTN, DSCRPTN, CRTN_TM, UPDT_TM, CRS_STT)
        VALUES (:id, :name, :section, :description, :creationTime, :updateTime, :courseState)
        ON CONFLICT(ID) DO UPDATE SET
            NM=excluded.NM,
            SCTN=excluded.SCTN,
            DSCRPTN=excluded.DSCRPTN,
            UPDT_TM=excluded.UPDT_TM,
            CRS_STT=excluded.CRS_STT;
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
        INSERT INTO ENRLLMNTS (CRS_ID, USR_ID, RL)
        VALUES (?, ?, ?)
        ON CONFLICT(CRS_ID, USR_ID) DO NOTHING;
    """, (course_id, user_id, role))

def save_announcement(conn: Connection, announcement: dict):
    """Saves a single announcement to the database."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ANNCMNTS (ID, CRS_ID, CRTR_USR_ID, TXT, STT, CRTN_TM, UPDT_TM)
        VALUES (:id, :courseId, :creatorUserId, :text, :state, :creationTime, :updateTime)
        ON CONFLICT(ID) DO UPDATE SET
            TXT=excluded.TXT,
            STT=excluded.STT,
            UPDT_TM=excluded.UPDT_TM;
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
        INSERT INTO CRS_WRK (ID, CRS_ID, TTL, DSCRPTN, WRK_TYP, MX_PNTS, CRTN_TM, UPDT_TM)
        VALUES (:id, :courseId, :title, :description, :workType, :maxPoints, :creationTime, :updateTime)
        ON CONFLICT(ID) DO UPDATE SET
            TTL=excluded.TTL,
            DSCRPTN=excluded.DSCRPTN,
            WRK_TYP=excluded.WRK_TYP,
            MX_PNTS=excluded.MX_PNTS,
            UPDT_TM=excluded.UPDT_TM;
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
        INSERT INTO STDNT_SBMSSNS (ID, CRS_WRK_ID, USR_ID, STT, ASSGND_GRD, DRFT_GRD, CRTN_TM, UPDT_TM)
        VALUES (:id, :courseWorkId, :userId, :state, :assignedGrade, :draftGrade, :creationTime, :updateTime)
        ON CONFLICT(ID) DO UPDATE SET
            STT=excluded.STT,
            ASSGND_GRD=excluded.ASSGND_GRD,
            DRFT_GRD=excluded.DRFT_GRD,
            UPDT_TM=excluded.UPDT_TM;
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

def create_views(conn: Connection):
    """
    Creates analytics views in the database.

    These views denormalize the data to make it easier to query for
    common analytical and investigative purposes.
    """
    cursor = conn.cursor()

    # View for Enrollment Details
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS VW_ENRLLMNT_DTLS AS
    SELECT
        c.NM AS CRS_NM,
        c.SCTN AS CRS_SCTN,
        u.NM AS USR_NM,
        u.EML AS USR_EML,
        e.RL AS USR_RL
    FROM ENRLLMNTS e
    JOIN USRS u ON e.USR_ID = u.ID
    JOIN CRSS c ON e.CRS_ID = c.ID;
    """)

    # View for Assignment Grades with explicit submission status
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS VW_ASSGNMNT_GRDS AS
    SELECT
        c.NM AS CRS_NM,
        cw.TTL AS ASSGNMNT_TTL,
        u.NM AS STNDT_NM,
        s.STT AS SBMSSN_STT_RAW,
        CASE
            WHEN s.STT = 'RETURNED' AND s.ASSGND_GRD IS NULL THEN 'EXCSD'
            WHEN s.STT = 'TURNED_IN' THEN 'SBMITD'
            WHEN s.STT = 'CREATED' THEN 'MSSNG'
            WHEN s.STT = 'NEW' THEN 'ASSGND'
            ELSE s.STT
        END AS SBMSSN_STS,
        s.ASSGND_GRD,
        s.UPDT_TM AS GRD_UPDT_TM
    FROM STDNT_SBMSSNS s
    JOIN USRS u ON s.USR_ID = u.ID
    JOIN CRS_WRK cw ON s.CRS_WRK_ID = cw.ID
    JOIN CRSS c ON cw.CRS_ID = c.ID;
    """)

    # View for a combined Course Activity Log
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS VW_CRS_ACTVTY_LG AS
    SELECT
        c.NM AS CRS_NM,
        cw.CRTN_TM AS ACTVTY_DT,
        'Assignment' as ACTVTY_TYP,
        cw.TTL AS TTL,
        u.NM AS CRTR_NM
    FROM CRS_WRK cw
    JOIN CRSS c ON cw.CRS_ID = c.ID
    LEFT JOIN USRS u ON cw.CRTR_USR_ID = u.ID -- Assuming creator might not exist for coursework
    UNION ALL
    SELECT
        c.NM AS CRS_NM,
        a.CRTN_TM AS ACTVTY_DT,
        'Announcement' as ACTVTY_TYP,
        a.TXT AS TTL,
        u.NM AS CRTR_NM
    FROM ANNCMNTS a
    JOIN CRSS c ON a.CRS_ID = c.ID
    JOIN USRS u ON a.CRTR_USR_ID = u.ID;
    """)

    # View for SIS Enrollment Roster
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS VW_SIS_ENRLLMNT_ROSTER AS
    SELECT
        e.CRS_ID,
        c.NM AS CRS_NM,
        e.USR_ID,
        u.EML AS USR_EML,
        e.RL
    FROM ENRLLMNTS e
    JOIN USRS u ON e.USR_ID = u.ID
    JOIN CRSS c ON e.CRS_ID = c.ID;
    """)

    conn.commit()
    print("Database views created successfully.")
