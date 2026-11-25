import sqlite3

def create_table():
    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            location TEXT,
            salary TEXT,
            application_date TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.execute('''
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
''')

    conn.commit()
    conn.close()


def add_application(user_id,company, position, location, salary,
                    application_date, status, description):

    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        INSERT INTO applications
        (user_id,company, position, location, salary,
         application_date, status, description)
        VALUES (?, ?, ?, ?, ?, ?, ?,?)
    ''', (user_id,company, position, location, salary,
          application_date, status, description))

   

    conn.commit()
    conn.close()

def get_applications(user_id):
    conn = sqlite3.connect('smarthire.db')
    conn.row_factory = sqlite3.Row

    applications = conn.execute(
        'SELECT * FROM applications WHERE user_id=? ORDER BY id DESC',(user_id,)
    ).fetchall()

    conn.close()
    return applications



def get_dashboard_stats(user_id):
    conn = sqlite3.connect('smarthire.db')

    stats = conn.execute('''
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN LOWER(TRIM(status)) = 'applied' THEN 1 ELSE 0 END) AS applied,
            SUM(CASE WHEN LOWER(TRIM(status)) = 'interview' THEN 1 ELSE 0 END) AS interviews,
            SUM(CASE WHEN LOWER(TRIM(status)) = 'selected' THEN 1 ELSE 0 END) AS selected,
            SUM(CASE WHEN LOWER(TRIM(status)) = 'offer received' THEN 1 ELSE 0 END) AS offers,
            SUM(CASE WHEN LOWER(TRIM(status)) = 'rejected' THEN 1 ELSE 0 END) AS rejected
        FROM applications
        WHERE user_id = ?
    ''',(user_id,)).fetchone()

    conn.close()

    return {
        'total': stats[0] or 0,
        'applied': stats[1] or 0,
        'interviews': stats[2] or 0,
        'selected': stats[3] or 0,
        'offers': stats[4] or 0,
        'rejected': stats[5] or 0
    }


# def fix_google_status():
#     conn = sqlite3.connect('smarthire.db')

#     conn.execute("""
#         UPDATE applications
#         SET status = 'Applied'
#         WHERE LOWER(company) = 'google'
#         AND (status IS NULL OR TRIM(status) = '')
#     """)

#     conn.commit()
#     conn.close()


def update_application(app_id,user_id, company, position, location,
                      salary, application_date, status, description):

    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        UPDATE applications
        SET company = ?,
            position = ?,
            location = ?,
            salary = ?,
            application_date = ?,
            status = ?,
            description = ?
        WHERE id = ? AND user_id = ?
    ''', (company, position, location, salary,
          application_date, status, description, app_id, user_id))

    conn.commit()
    conn.close()


def delete_application(app_id, user_id):

    conn = sqlite3.connect('smarthire.db')

    conn.execute(
        'DELETE FROM applications WHERE id = ? AND user_id = ?',
        (app_id, user_id)
    )

    conn.commit()
    conn.close()

def get_application_by_id(app_id, user_id):
    conn = sqlite3.connect('smarthire.db')
    conn.row_factory = sqlite3.Row

    application = conn.execute(
        'SELECT * FROM applications WHERE id = ? AND user_id = ?',
        (app_id, user_id)
    ).fetchone()

    conn.close()
    return application


def create_user(username, email, password):
    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    ''', (username, email, password))

    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = sqlite3.connect('smarthire.db')
    conn.row_factory = sqlite3.Row

    user = conn.execute(
        'SELECT * FROM users WHERE email = ?',
        (email,)
    ).fetchone()

    conn.close()
    return user


def add_user_id_column():
    conn = sqlite3.connect('smarthire.db')

    columns = conn.execute(
        "PRAGMA table_info(applications)"
    ).fetchall()

    column_names = [column[1] for column in columns]

    if 'user_id' not in column_names:
        conn.execute(
            'ALTER TABLE applications ADD COLUMN user_id INTEGER'
        )

    conn.commit()
    conn.close()

def assign_existing_applications(user_id):
    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        UPDATE applications
        SET user_id = ?
        WHERE user_id IS NULL
    ''', (user_id,))

    conn.commit()
    conn.close()


def add_interview(user_id, application_id, interview_date,
                  interview_time, interview_type, interview_round,
                  interviewer, meeting_link, status, notes):

    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        INSERT INTO interviews
        (user_id, application_id, interview_date, interview_time,
         interview_type, interview_round, interviewer,
         meeting_link, status, notes)
        SELECT ?, id, ?, ?, ?, ?, ?, ?, ?, ?
        FROM applications
        WHERE id = ? AND user_id = ?
    ''', (
        user_id, interview_date, interview_time,
        interview_type, interview_round, interviewer,
        meeting_link, status, notes, application_id, user_id
    ))

    conn.commit()
    conn.close()


def get_interviews(user_id):

    conn = sqlite3.connect('smarthire.db')
    conn.row_factory = sqlite3.Row

    interviews = conn.execute('''
        SELECT interviews.*, applications.company,
               applications.position
        FROM interviews
        JOIN applications
        ON interviews.application_id = applications.id
        WHERE interviews.user_id = ?
        ORDER BY interviews.interview_date ASC
    ''', (user_id,)).fetchall()

    conn.close()
    return interviews


def get_interview_by_id(interview_id, user_id):

    conn = sqlite3.connect('smarthire.db')
    conn.row_factory = sqlite3.Row

    interview = conn.execute('''
        SELECT interviews.*, applications.company,
               applications.position
        FROM interviews
        JOIN applications
        ON interviews.application_id = applications.id
        WHERE interviews.id = ? AND interviews.user_id = ?
    ''', (interview_id, user_id)).fetchone()

    conn.close()
    return interview


def delete_interview(interview_id, user_id):

    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        DELETE FROM interviews
        WHERE id = ? AND user_id = ?
    ''', (interview_id, user_id))

    conn.commit()
    conn.close()

def update_interview(interview_id, user_id, application_id,
                     interview_date, interview_time,
                     interview_type, interview_round,
                     interviewer, meeting_link, status, notes):

    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        UPDATE interviews
        SET application_id = ?,
            interview_date = ?,
            interview_time = ?,
            interview_type = ?,
            interview_round = ?,
            interviewer = ?,
            meeting_link = ?,
            status = ?,
            notes = ?
        WHERE id = ? AND user_id = ?
        AND EXISTS (
            SELECT 1 FROM applications
            WHERE applications.id = ?
            AND applications.user_id = ?
        )
    ''', (
        application_id, interview_date, interview_time,
        interview_type, interview_round, interviewer,
        meeting_link, status, notes,
        interview_id, user_id, application_id, user_id
    ))

    conn.commit()
    conn.close()


def get_user_by_id(user_id):
    conn = sqlite3.connect('smarthire.db')
    conn.row_factory = sqlite3.Row

    user = conn.execute(
        'SELECT id, username, email, password FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()

    conn.close()
    return user


def update_user_profile(user_id, username, email):
    conn = sqlite3.connect('smarthire.db')

    existing_user = conn.execute(
        'SELECT id FROM users WHERE email = ? AND id != ?',
        (email, user_id)
    ).fetchone()

    if existing_user:
        conn.close()
        return False

    conn.execute('''
        UPDATE users
        SET username = ?, email = ?
        WHERE id = ?
    ''', (username, email, user_id))

    conn.commit()
    conn.close()
    return True


def update_user_password(user_id, new_password):
    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        UPDATE users
        SET password = ?
        WHERE id = ?
    ''', (new_password, user_id))

    conn.commit()
    conn.close()



def create_settings_table():
    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            email_notifications INTEGER NOT NULL DEFAULT 1,
            interview_reminders INTEGER NOT NULL DEFAULT 1,
            application_updates INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


def get_user_settings(user_id):
    conn = sqlite3.connect('smarthire.db')
    conn.row_factory = sqlite3.Row

    conn.execute('''
        INSERT OR IGNORE INTO user_settings (user_id)
        VALUES (?)
    ''', (user_id,))

    conn.commit()

    settings = conn.execute('''
        SELECT * FROM user_settings
        WHERE user_id = ?
    ''', (user_id,)).fetchone()

    conn.close()
    return settings


def update_user_settings(user_id, email_notifications,
                         interview_reminders, application_updates):

    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        INSERT OR IGNORE INTO user_settings (user_id)
        VALUES (?)
    ''', (user_id,))

    conn.execute('''
        UPDATE user_settings
        SET email_notifications = ?,
            interview_reminders = ?,
            application_updates = ?
        WHERE user_id = ?
    ''', (
        email_notifications,
        interview_reminders,
        application_updates,
        user_id
    ))

    conn.commit()
    conn.close()


# NOTIFICATIONS TABLE

def create_notifications_table():

    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
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
    ''')

    conn.commit()
    conn.close()


# ADD NOTIFICATION

def add_notification(user_id, title, message,
                     notification_type='general'):

    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        INSERT INTO notifications
        (user_id, title, message, notification_type)
        VALUES (?, ?, ?, ?)
    ''', (user_id, title, message, notification_type))

    conn.commit()
    conn.close()


# GET USER NOTIFICATIONS

def get_notifications(user_id):

    conn = sqlite3.connect('smarthire.db')
    conn.row_factory = sqlite3.Row

    notifications = conn.execute('''
        SELECT *
        FROM notifications
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
    ''', (user_id,)).fetchall()

    conn.close()

    return notifications


# COUNT UNREAD NOTIFICATIONS

def get_unread_notification_count(user_id):

    conn = sqlite3.connect('smarthire.db')

    count = conn.execute('''
        SELECT COUNT(*)
        FROM notifications
        WHERE user_id = ? AND is_read = 0
    ''', (user_id,)).fetchone()[0]

    conn.close()

    return count


# MARK NOTIFICATION AS READ

def mark_notification_read(notification_id, user_id):

    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        UPDATE notifications
        SET is_read = 1
        WHERE id = ? AND user_id = ?
    ''', (notification_id, user_id))

    conn.commit()
    conn.close()


# DELETE NOTIFICATION

def delete_notification(notification_id, user_id):

    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        DELETE FROM notifications
        WHERE id = ? AND user_id = ?
    ''', (notification_id, user_id))

    conn.commit()
    conn.close()



def create_database_indexes():
    conn = sqlite3.connect('smarthire.db')

    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_applications_user
        ON applications(user_id)
    ''')

    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_interviews_user
        ON interviews(user_id)
    ''')

    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_interviews_date
        ON interviews(interview_date)
    ''')

    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_notifications_user
        ON notifications(user_id)
    ''')

    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_notifications_unread
        ON notifications(user_id, is_read)
    ''')

    conn.commit()
    conn.close()
