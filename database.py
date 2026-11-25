import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()


def _use_postgres():
    """Use PostgreSQL only when DATABASE_URL is set and USE_SQLITE is not enabled."""
    use_sqlite = os.getenv("USE_SQLITE", "").strip().lower()
    return bool(os.getenv("DATABASE_URL")) and use_sqlite not in ("1", "true", "yes")


def get_connection():
    """Create a connection to the selected database."""
    if _use_postgres():
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(
            os.environ["DATABASE_URL"],
            row_factory=dict_row,
            connect_timeout=15,
        )

    conn = sqlite3.connect("smarthire.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _execute(conn, query, params=()):
    """Run a query with the placeholder style required by the selected database."""
    if _use_postgres():
        query = query.replace("?", "%s")
    return conn.execute(query, params)


def create_table():
    conn = get_connection()
    try:
        if _use_postgres():
            conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    company TEXT NOT NULL,
                    position TEXT NOT NULL,
                    location TEXT,
                    salary TEXT,
                    application_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    description TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interviews (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    application_id INTEGER NOT NULL REFERENCES applications(id),
                    interview_date TEXT NOT NULL,
                    interview_time TEXT,
                    interview_type TEXT,
                    interview_round TEXT,
                    interviewer TEXT,
                    meeting_link TEXT,
                    status TEXT DEFAULT 'Scheduled',
                    notes TEXT
                )
            """)
        else:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    company TEXT NOT NULL,
                    position TEXT NOT NULL,
                    location TEXT,
                    salary TEXT,
                    application_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    description TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    application_id INTEGER NOT NULL,
                    interview_date TEXT NOT NULL,
                    interview_time TEXT,
                    interview_type TEXT,
                    interview_round TEXT,
                    interviewer TEXT,
                    meeting_link TEXT,
                    status TEXT DEFAULT 'Scheduled',
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (application_id) REFERENCES applications(id)
                )
            """)
        conn.commit()
    finally:
        conn.close()


def add_application(user_id, company, position, location, salary,
                    application_date, status, description):
    conn = get_connection()
    try:
        _execute(conn, """
            INSERT INTO applications
            (user_id, company, position, location, salary,
             application_date, status, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, company, position, location, salary,
              application_date, status, description))
        conn.commit()
    finally:
        conn.close()


def get_applications(user_id):
    conn = get_connection()
    try:
        return _execute(conn, """
            SELECT * FROM applications
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()
    finally:
        conn.close()


def get_dashboard_stats(user_id):
    conn = get_connection()
    try:
        stats = _execute(conn, """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN LOWER(TRIM(status)) = 'applied' THEN 1 ELSE 0 END) AS applied,
                SUM(CASE WHEN LOWER(TRIM(status)) = 'interview' THEN 1 ELSE 0 END) AS interviews,
                SUM(CASE WHEN LOWER(TRIM(status)) = 'selected' THEN 1 ELSE 0 END) AS selected,
                SUM(CASE WHEN LOWER(TRIM(status)) = 'offer received' THEN 1 ELSE 0 END) AS offers,
                SUM(CASE WHEN LOWER(TRIM(status)) = 'rejected' THEN 1 ELSE 0 END) AS rejected
            FROM applications
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        return {
            "total": stats["total"] or 0,
            "applied": stats["applied"] or 0,
            "interviews": stats["interviews"] or 0,
            "selected": stats["selected"] or 0,
            "offers": stats["offers"] or 0,
            "rejected": stats["rejected"] or 0,
        }
    finally:
        conn.close()


def update_application(app_id, user_id, company, position, location,
                       salary, application_date, status, description):
    conn = get_connection()
    try:
        _execute(conn, """
            UPDATE applications
            SET company = ?, position = ?, location = ?, salary = ?,
                application_date = ?, status = ?, description = ?
            WHERE id = ? AND user_id = ?
        """, (company, position, location, salary, application_date,
              status, description, app_id, user_id))
        conn.commit()
    finally:
        conn.close()


def delete_application(app_id, user_id):
    conn = get_connection()
    try:
        _execute(conn, """
            DELETE FROM applications WHERE id = ? AND user_id = ?
        """, (app_id, user_id))
        conn.commit()
    finally:
        conn.close()


def get_application_by_id(app_id, user_id):
    conn = get_connection()
    try:
        return _execute(conn, """
            SELECT * FROM applications WHERE id = ? AND user_id = ?
        """, (app_id, user_id)).fetchone()
    finally:
        conn.close()


def create_user(username, email, password):
    conn = get_connection()
    try:
        _execute(conn, """
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, password))
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    try:
        return _execute(conn, """
            SELECT * FROM users WHERE email = ?
        """, (email,)).fetchone()
    finally:
        conn.close()


def add_user_id_column():
    conn = get_connection()
    try:
        if _use_postgres():
            conn.execute("""
                ALTER TABLE applications
                ADD COLUMN IF NOT EXISTS user_id INTEGER
            """)
        else:
            columns = conn.execute("PRAGMA table_info(applications)").fetchall()
            column_names = [column["name"] for column in columns]
            if "user_id" not in column_names:
                conn.execute(
                    "ALTER TABLE applications ADD COLUMN user_id INTEGER"
                )
        conn.commit()
    finally:
        conn.close()


def assign_existing_applications(user_id):
    conn = get_connection()
    try:
        _execute(conn, """
            UPDATE applications SET user_id = ?
            WHERE user_id IS NULL
        """, (user_id,))
        conn.commit()
    finally:
        conn.close()


def add_interview(user_id, application_id, interview_date,
                  interview_time, interview_type, interview_round,
                  interviewer, meeting_link, status, notes):
    conn = get_connection()
    try:
        _execute(conn, """
            INSERT INTO interviews
            (user_id, application_id, interview_date, interview_time,
             interview_type, interview_round, interviewer,
             meeting_link, status, notes)
            SELECT ?, id, ?, ?, ?, ?, ?, ?, ?, ?
            FROM applications
            WHERE id = ? AND user_id = ?
        """, (user_id, interview_date, interview_time, interview_type,
              interview_round, interviewer, meeting_link, status, notes,
              application_id, user_id))
        conn.commit()
    finally:
        conn.close()


def get_interviews(user_id):
    conn = get_connection()
    try:
        return _execute(conn, """
            SELECT interviews.*, applications.company, applications.position
            FROM interviews
            JOIN applications ON interviews.application_id = applications.id
            WHERE interviews.user_id = ?
            ORDER BY interviews.interview_date ASC
        """, (user_id,)).fetchall()
    finally:
        conn.close()


def get_interview_by_id(interview_id, user_id):
    conn = get_connection()
    try:
        return _execute(conn, """
            SELECT interviews.*, applications.company, applications.position
            FROM interviews
            JOIN applications ON interviews.application_id = applications.id
            WHERE interviews.id = ? AND interviews.user_id = ?
        """, (interview_id, user_id)).fetchone()
    finally:
        conn.close()


def delete_interview(interview_id, user_id):
    conn = get_connection()
    try:
        _execute(conn, """
            DELETE FROM interviews WHERE id = ? AND user_id = ?
        """, (interview_id, user_id))
        conn.commit()
    finally:
        conn.close()


def update_interview(interview_id, user_id, application_id,
                     interview_date, interview_time, interview_type,
                     interview_round, interviewer, meeting_link, status, notes):
    conn = get_connection()
    try:
        _execute(conn, """
            UPDATE interviews
            SET application_id = ?, interview_date = ?, interview_time = ?,
                interview_type = ?, interview_round = ?, interviewer = ?,
                meeting_link = ?, status = ?, notes = ?
            WHERE id = ? AND user_id = ?
            AND EXISTS (
                SELECT 1 FROM applications
                WHERE applications.id = ? AND applications.user_id = ?
            )
        """, (application_id, interview_date, interview_time, interview_type,
              interview_round, interviewer, meeting_link, status, notes,
              interview_id, user_id, application_id, user_id))
        conn.commit()
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_connection()
    try:
        return _execute(conn, """
            SELECT id, username, email, password
            FROM users WHERE id = ?
        """, (user_id,)).fetchone()
    finally:
        conn.close()


def update_user_profile(user_id, username, email):
    conn = get_connection()
    try:
        existing_user = _execute(conn, """
            SELECT id FROM users WHERE email = ? AND id != ?
        """, (email, user_id)).fetchone()

        if existing_user:
            return False

        _execute(conn, """
            UPDATE users SET username = ?, email = ?
            WHERE id = ?
        """, (username, email, user_id))
        conn.commit()
        return True
    finally:
        conn.close()


def update_user_password(user_id, new_password):
    conn = get_connection()
    try:
        _execute(conn, """
            UPDATE users SET password = ? WHERE id = ?
        """, (new_password, user_id))
        conn.commit()
    finally:
        conn.close()


def create_settings_table():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                email_notifications INTEGER NOT NULL DEFAULT 1,
                interview_reminders INTEGER NOT NULL DEFAULT 1,
                application_updates INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
    finally:
        conn.close()


def get_user_settings(user_id):
    conn = get_connection()
    try:
        if _use_postgres():
            _execute(conn, """
                INSERT INTO user_settings (user_id) VALUES (?)
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id,))
        else:
            _execute(conn, """
                INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)
            """, (user_id,))
        conn.commit()
        return _execute(conn, """
            SELECT * FROM user_settings WHERE user_id = ?
        """, (user_id,)).fetchone()
    finally:
        conn.close()


def update_user_settings(user_id, email_notifications,
                         interview_reminders, application_updates):
    conn = get_connection()
    try:
        if _use_postgres():
            _execute(conn, """
                INSERT INTO user_settings (user_id) VALUES (?)
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id,))
        else:
            _execute(conn, """
                INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)
            """, (user_id,))

        _execute(conn, """
            UPDATE user_settings
            SET email_notifications = ?, interview_reminders = ?,
                application_updates = ?
            WHERE user_id = ?
        """, (email_notifications, interview_reminders,
              application_updates, user_id))
        conn.commit()
    finally:
        conn.close()


def create_notifications_table():
    conn = get_connection()
    try:
        if _use_postgres():
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    notification_type TEXT DEFAULT 'general',
                    is_read INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    notification_type TEXT DEFAULT 'general',
                    is_read INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
        conn.commit()
    finally:
        conn.close()


def add_notification(user_id, title, message, notification_type="general"):
    conn = get_connection()
    try:
        _execute(conn, """
            INSERT INTO notifications
            (user_id, title, message, notification_type)
            VALUES (?, ?, ?, ?)
        """, (user_id, title, message, notification_type))
        conn.commit()
    finally:
        conn.close()


def get_notifications(user_id):
    conn = get_connection()
    try:
        return _execute(conn, """
            SELECT * FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
        """, (user_id,)).fetchall()
    finally:
        conn.close()


def get_unread_notification_count(user_id):
    conn = get_connection()
    try:
        row = _execute(conn, """
            SELECT COUNT(*) AS count FROM notifications
            WHERE user_id = ? AND is_read = 0
        """, (user_id,)).fetchone()
        return row["count"]
    finally:
        conn.close()


def mark_notification_read(notification_id, user_id):
    conn = get_connection()
    try:
        _execute(conn, """
            UPDATE notifications SET is_read = 1
            WHERE id = ? AND user_id = ?
        """, (notification_id, user_id))
        conn.commit()
    finally:
        conn.close()


def delete_notification(notification_id, user_id):
    conn = get_connection()
    try:
        _execute(conn, """
            DELETE FROM notifications WHERE id = ? AND user_id = ?
        """, (notification_id, user_id))
        conn.commit()
    finally:
        conn.close()


def create_database_indexes():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_applications_user
            ON applications(user_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_interviews_user
            ON interviews(user_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_interviews_date
            ON interviews(interview_date)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user
            ON notifications(user_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_unread
            ON notifications(user_id, is_read)
        """)
        conn.commit()
    finally:
        conn.close()
