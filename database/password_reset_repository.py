import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "khansco.db"


class PasswordResetRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                status TEXT,
                request_date TEXT
            )
        """)
        self.conn.commit()

    def create_request(self, username):
        self.cursor.execute("""
            INSERT INTO password_reset_requests
            (
                username,
                status,
                request_date
            )
            VALUES (?, ?, ?)
        """, (
            username,
            "Pending",
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ))
        self.conn.commit()

    def get_requests(self):
        self.cursor.execute("""
            SELECT
                id,
                username,
                status,
                request_date
            FROM password_reset_requests
            ORDER BY id DESC
        """)
        return self.cursor.fetchall()

    def approve_request(self, request_id, new_password):
        self.cursor.execute("""
            SELECT username
            FROM password_reset_requests
            WHERE id = ?
        """, (request_id,))

        row = self.cursor.fetchone()

        if not row:
            return

        username = row[0]

        hashed = hashlib.sha256(new_password.encode()).hexdigest()

        self.cursor.execute("""
            UPDATE client_logins
            SET password = ?
            WHERE username = ?
        """, (
            hashed,
            username
        ))

        self.cursor.execute("""
            UPDATE password_reset_requests
            SET status = 'Completed'
            WHERE id = ?
        """, (request_id,))

        self.conn.commit()