# sore.py

import sqlite3
from datetime import datetime, date


DB_NAME = "email_logs.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            check_time TEXT,
            email_count INTEGER,
            last_sender TEXT,
            last_subject TEXT,
            last_received_time TEXT,
            is_read INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def insert_email_check(email_count, last_sender, last_subject, last_received_time=None):
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO email_checks (check_time, email_count, last_sender, last_subject, last_received_time)
        VALUES (?, ?, ?, ?, ?)
    """, (now, email_count, last_sender, last_subject, last_received_time))
    conn.commit()
    conn.close()


def get_unread_emails_today():
    today_str = date.today().isoformat()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT last_sender, last_subject FROM email_checks
        WHERE DATE(check_time) = ? AND is_read = 0
    """, (today_str,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def mark_last_as_read():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM email_checks
        WHERE is_read = 0
        ORDER BY id DESC LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        cursor.execute("""
            UPDATE email_checks SET is_read = 1 WHERE id = ?
        """, (result[0],))
        conn.commit()
    conn.close()
    
def get_last_db_record():
    import sqlite3
    conn = sqlite3.connect("email_logs.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email_count, last_sender, last_subject
        FROM email_checks
        ORDER BY id DESC LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, "", "")


# Ensure DB and table are initialized
init_db()