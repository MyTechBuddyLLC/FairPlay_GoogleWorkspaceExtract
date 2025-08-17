# FairPlay Google Workspace Extract

The FairPlay Google Workspace Extract is a standalone Python application designed to extract comprehensive data from a Google Workspace's Google Classroom instance. It stores the data in a local, normalized SQLite database, making it suitable for data analysis, auditing, and reporting.

The tool is designed with school IT administrators in mind and includes features for masking Personally Identifiable Information (PII) to protect student and teacher privacy.

## Features

*   **Comprehensive Data Extraction:** Extracts courses, teachers, students, enrollments, assignments, announcements, and student submissions.
*   **Local Storage:** Saves all data into a local SQLite database file, giving you full control over your data.
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
2.  Click the project drop-down menu at the top of the page and click **New Project**.
3.  Give your project a name (e.g., "Classroom Data Extractor") and click **Create**.

### B. Enable the Google Classroom API

1.  With your new project selected, navigate to the **APIs & Services > Library** section from the left-hand menu.
2.  Search for "Google Classroom API" and click on it.
3.  Click the **Enable** button.

### C. Create a Service Account

1.  In the Cloud Console, navigate to **APIs & Services > Credentials**.
2.  Click **+ Create Credentials** and select **Service account**.
3.  Give the service account a name (e.g., "classroom-extractor-sa") and a description.
4.  Click **Create and Continue**. You do not need to grant this service account any roles on the GCP project. Click **Continue**, then **Done**.

### D. Create and Download Service Account Keys

1.  On the Credentials screen, find the service account you just created and click on it.
2.  Go to the **Keys** tab.
3.  Click **Add Key > Create new key**.
4.  Select **JSON** as the key type and click **Create**.
5.  A JSON file will be downloaded to your computer. **This file is highly sensitive!** Treat it like a password.
6.  Rename the downloaded file to `credentials.json` and move it into the root directory of this project.

### E. Grant Domain-Wide Delegation

1.  Go back to the details page for your service account in the Cloud Console (from step D).
2.  Under the **Advanced settings** section, find the **Unique ID** and copy it. It will be a long number.
3.  Now, go to your [Google Workspace Admin console](https://admin.google.com/).
4.  From the left-hand menu, navigate to **Security > Access and data control > API controls**.
5.  Under "Domain-wide Delegation", click **Manage Domain-Wide Delegation**.
6.  Click **Add new**.
7.  In the **Client ID** field, paste the **Unique ID** you copied in step E.2.
8.  In the **OAuth scopes** field, paste the following comma-separated list of scopes. These are all read-only.
    ```
    https://www.googleapis.com/auth/classroom.courses.readonly,https://www.googleapis.com/auth/classroom.rosters.readonly,https://www.googleapis.com/auth/classroom.coursework.me.readonly,https://www.googleapis.com/auth/classroom.coursework.students.readonly,https://www.googleapis.com/auth/classroom.student-submissions.students.readonly,https://www.googleapis.com/auth/classroom.announcements.readonly,https://www.googleapis.com/auth/classroom.profile.emails,https://www.googleapis.com/auth/classroom.profile.photos
    ```
9.  Click **Authorize**. The setup is now complete.

## Configuration

Before running the application, you need to create your own configuration file.

1.  Copy the example configuration file:
    ```bash
    cp config.ini.example config.ini
    ```
2.  Open `config.ini` in a text editor and fill in the values:

    *   `SERVICE_ACCOUNT_FILE`: The path to your credentials file. If you followed the instructions above, this should be `credentials.json`.
    *   `ADMIN_USER_EMAIL`: The email address of a Google Workspace administrator. The script will impersonate this user to access all classroom data.
    *   `PATH`: The file name for the SQLite database that will be created (e.g., `classroom_data.sqlite3`).
    *   `PII_MASKING_LEVEL`: Set the desired level of PII masking.
        *   `none`: (Default) All data is stored as is.
        *   `students_only`: Masks the name and email of all users with the "student" role.
        *   `all`: Masks the name and email of all users (students and teachers).

## Running the Application

Once everything is configured, run the script from the project's root directory:
```bash
python main.py
```
The script will print its progress to the console. When it is finished, you will find the SQLite database file (e.g., `classroom_data.sqlite3`) in the project directory. You can then use any SQLite-compatible tool to view and analyze the data.

## Database Schema

The generated database contains the following tables:
*   `users`: Stores all unique users (teachers and students).
*   `courses`: Information about each classroom.
*   `enrollments`: Links users to the courses they are enrolled in and specifies their role.
*   `announcements`: All announcements made in each course.
*   `course_work`: All assignments and other course work.
*   `student_submissions`: Records of student submissions for each piece of course work, including grades.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
