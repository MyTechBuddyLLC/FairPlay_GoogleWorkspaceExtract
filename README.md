# FairPlay Google Workspace Extract

The FairPlay Google Workspace Extract is a standalone Python application designed to extract comprehensive data from a Google Workspace's Google Classroom instance. It stores the data in a local, normalized SQLite database, making it suitable for data analysis, auditing, and reporting.

The tool is designed with school IT administrators in mind and includes features for masking Personally Identifiable Information (PII) to protect student and teacher privacy. After the data is extracted, a set of pre-built database views are created to simplify common analytical and investigative queries.

## Features

*   **Comprehensive Data Extraction:** Extracts courses, teachers, students, enrollments, assignments, announcements, and student submissions.
*   **Local Storage:** Saves all data into a local SQLite database file, giving you full control over your data.
*   **Analytics-Ready Views:** Automatically creates several database views that join tables and denormalize data for easier querying.
*   **Normalized Database:** The database schema is designed in Third Normal Form (3NF) for data integrity and efficient querying.
*   **PII Masking:** Built-in functionality to mask student or all user (student and teacher) PII, replacing names and emails with non-identifiable unique IDs.
*   **Standalone and Configurable:** Runs as a standalone script with all settings managed through a simple configuration file.

## Prerequisites

*   Python 3.8 or newer.
*   Administrator access to a Google Workspace account. This is required to grant the necessary permissions for the tool to access Classroom data across your domain.

## Setup and Installation

### Step 1: Clone the Repository
First, clone this repository to your local machine using git:
```bash
git clone https://github.com/your-repo/FairPlay_GoogleWorkspaceExtract.git
cd FairPlay_GoogleWorkspaceExtract
```

### Step 2: Install Dependencies
Install the necessary Python libraries using pip and the provided `requirements.txt` file:
```bash
pip install -r requirements.txt
```

## Google Workspace Authentication Setup
This is the most critical part of the setup process. This tool uses a **Service Account** with **Domain-Wide Delegation** to access Google Classroom data on behalf of an administrator. This allows the script to see all classrooms in your domain without needing to log in as a specific user.

Follow these steps carefully.

### A. Create a Google Cloud Project
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Click the project drop-down and click **New Project**.
3.  Give the project a name (e.g., "Classroom Data Extractor") and click **Create**.

### B. Enable the Google Classroom API
1.  With your new project selected, navigate to **APIs & Services > Library**.
2.  Search for "Google Classroom API" and click on it.
3.  Click **Enable**.

### C. Create a Service Account
1.  In the Cloud Console, navigate to **APIs & Services > Credentials**.
2.  Click **+ Create Credentials** and select **Service account**.
3.  Give the service account a name (e.g., "classroom-extractor-sa").
4.  Click **Create and Continue**, then **Done**. You do not need to grant this service account any roles.

### D. Create and Download Service Account Keys
1.  On the Credentials screen, find and click on the service account you just created.
2.  Go to the **Keys** tab, click **Add Key > Create new key**.
3.  Select **JSON** and click **Create**.
4.  A JSON file will be downloaded. **This file is highly sensitive!**
5.  Rename it to `credentials.json` and place it in the root directory of this project.

### E. Grant Domain-Wide Delegation
1.  Back in the service account details page, find and copy the **Unique ID** under the **Advanced settings** section.
2.  Go to your [Google Workspace Admin console](https://admin.google.com/).
3.  Navigate to **Security > Access and data control > API controls**.
4.  Under "Domain-wide Delegation", click **Manage Domain-Wide Delegation**.
5.  Click **Add new**, paste the **Client ID**, and add the following OAuth scopes:
    ```
    https://www.googleapis.com/auth/classroom.courses.readonly,https://www.googleapis.com/auth/classroom.rosters.readonly,https://www.googleapis.com/auth/classroom.coursework.me.readonly,https://www.googleapis.com/auth/classroom.coursework.students.readonly,https://www.googleapis.com/auth/classroom.student-submissions.students.readonly,https://www.googleapis.com/auth/classroom.announcements.readonly,https://www.googleapis.com/auth/classroom.profile.emails,https://www.googleapis.com/auth/classroom.profile.photos
    ```
6.  Click **Authorize**.

## Configuration

Copy the example configuration file and edit it:
```bash
cp config.ini.example config.ini
```
*   `SERVICE_ACCOUNT_FILE`: Path to your `credentials.json` file. If it's in the same directory as the script, the filename is sufficient.
*   `ADMIN_USER_EMAIL`: The email of a Workspace administrator for the script to impersonate.
*   `PATH`: The path for the output SQLite database (e.g., `data/classroom_data.sqlite3`). The script will create directories if they don't exist.
*   `PII_MASKING_LEVEL`: Set the PII masking level: `none`, `students_only`, or `all`.
     *   `none`: (Default) All data is stored as is.
     *   `students_only`: Masks the name and email of all users with the "student" role.
     *   `all`: Masks the name and email of all users (students and teachers).

## Running the Application

Run the script from the project's root directory:
```bash
python main.py
```
The script will print its progress. When finished, you will find the SQLite database file at the path you specified.

## Database Schema

The generated database contains the following tables with a naming convention that removes vowels (except the first) and uses all caps.

*   **`USRS`**: Stores all unique users.
    *   `ID`, `NM`, `EML`, `PHT_URL`
*   **`CRSS`**: Information about each classroom.
    *   `ID`, `NM`, `SCTN`, `DSCRPTN`, `CRTN_TM`, `UPDT_TM`, `CRS_STT`
*   **`ENRLLMNTS`**: Links users to courses with a specific role.
    *   `ENRLLMNT_ID`, `CRS_ID`, `USR_ID`, `RL`
*   **`ANNCMNTS`**: Announcements made in each course.
    *   `ID`, `CRS_ID`, `CRTR_USR_ID`, `TXT`, `STT`, `CRTN_TM`, `UPDT_TM`
*   **`CRS_WRK`**: Assignments and other course work.
    *   `ID`, `CRS_ID`, `TTL`, `DSCRPTN`, `WRK_TYP`, `MX_PNTS`, `CRTN_TM`, `UPDT_TM`
*   **`STDNT_SBMSSNS`**: Records of student submissions for course work.
    *   `ID`, `CRS_WRK_ID`, `USR_ID`, `STT`, `ASSGND_GRD`, `DRFT_GRD`, `CRTN_TM`, `UPDT_TM`

## Database Views for Analytics

To simplify analytics, four views are automatically created.

### `VW_ENRLLMNT_DTLS`
*   **Purpose:** Provides a simple, human-readable roster for each course.
*   **Columns:** `CRS_NM`, `CRS_SCTN`, `USR_NM`, `USR_EML`, `USR_RL`
*   **Example Query:** `SELECT * FROM VW_ENRLLMNT_DTLS WHERE CRS_NM = 'Biology 101';`

### `VW_ASSGNMNT_GRDS`
*   **Purpose:** The core view for grade-related investigations. Provides a flat list of every student's submission for every assignment.
*   **Columns:** `CRS_NM`, `ASSGNMNT_TTL`, `STNDT_NM`, `SBMSSN_STT_RAW`, `SBMSSN_STS` (a simplified status: EXCSD, SBMITD, MSSNG, ASSGND), `ASSGND_GRD`, `GRD_UPDT_TM`
*   **Example Query (find excused assignments):** `SELECT * FROM VW_ASSGNMNT_GRDS WHERE SBMSSN_STS = 'EXCSD';`

### `VW_CRS_ACTVTY_LG`
*   **Purpose:** Provides a chronological log of all major events (assignments and announcements) in a course.
*   **Columns:** `CRS_NM`, `ACTVTY_DT`, `ACTVTY_TYP` ('Assignment' or 'Announcement'), `TTL`, `CRTR_NM`
*   **Example Query:** `SELECT * FROM VW_CRS_ACTVTY_LG WHERE CRS_NM = 'History 202' ORDER BY ACTVTY_DT DESC;`

### `VW_SIS_ENRLLMNT_ROSTER`
*   **Purpose:** Provides a clean, ID-based roster perfect for syncing with a Student Information System (SIS).
*   **Columns:** `CRS_ID`, `CRS_NM`, `USR_ID`, `USR_EML`, `RL`
*   **Example Query:** `SELECT * FROM VW_SIS_ENRLLMNT_ROSTER;`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
