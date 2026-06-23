import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "khansco.db"


class ClientPortalRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_logins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                username TEXT UNIQUE,
                password TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                document_name TEXT,
                file_name TEXT,
                upload_date TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                work_title TEXT,
                status TEXT,
                remarks TEXT,
                updated_date TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                status TEXT,
                created_date TEXT
            )
        """)

        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_client(self, client_name, mobile, email, username, password):
        self.cursor.execute("""
            INSERT INTO clients
            (
                client_code,
                client_name,
                gstin,
                mobile,
                email,
                assigned_staff
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            client_name,
            "",
            mobile,
            email,
            ""
        ))

        client_id = self.cursor.lastrowid

        self.cursor.execute("""
            INSERT INTO client_logins
            (
                client_id,
                username,
                password
            )
            VALUES (?, ?, ?)
        """, (
            client_id,
            username,
            self.hash_password(password)
        ))

        self.cursor.execute("""
            INSERT INTO notifications
            (
                message,
                status,
                created_date
            )
            VALUES (?, ?, ?)
        """, (
            f"New client registered: {client_name}",
            "Unread",
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ))

        self.conn.commit()

    def verify_client_login(self, username, password):
        self.cursor.execute("""
            SELECT
                client_logins.client_id,
                clients.client_name
            FROM client_logins
            JOIN clients ON client_logins.client_id = clients.id
            WHERE client_logins.username = ?
            AND client_logins.password = ?
        """, (
            username,
            self.hash_password(password)
        ))

        return self.cursor.fetchone()

    def save_document(self, client_id, document_name, file_name):
        self.cursor.execute("""
            INSERT INTO client_documents
            (
                client_id,
                document_name,
                file_name,
                upload_date
            )
            VALUES (?, ?, ?, ?)
        """, (
            client_id,
            document_name,
            file_name,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ))

        self.conn.commit()

    def get_client_documents(self, client_id):
        self.cursor.execute("""
            SELECT
                document_name,
                file_name,
                upload_date
            FROM client_documents
            WHERE client_id = ?
            ORDER BY id DESC
        """, (client_id,))

        return self.cursor.fetchall()

    def get_all_documents(self):
        self.cursor.execute("""
            SELECT
                client_documents.id,
                clients.client_name,
                client_documents.document_name,
                client_documents.file_name,
                client_documents.upload_date
            FROM client_documents
            JOIN clients ON client_documents.client_id = clients.id
            ORDER BY client_documents.id DESC
        """)

        return self.cursor.fetchall()

    def get_clients(self):
        self.cursor.execute("""
            SELECT id, client_name
            FROM clients
            ORDER BY client_name
        """)

        return self.cursor.fetchall()

    def add_work_progress(self, client_id, work_title, status, remarks):
        self.cursor.execute("""
            INSERT INTO work_progress
            (
                client_id,
                work_title,
                status,
                remarks,
                updated_date
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            client_id,
            work_title,
            status,
            remarks,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ))

        self.conn.commit()

    def get_client_progress(self, client_id):
        self.cursor.execute("""
            SELECT
                work_title,
                status,
                remarks,
                updated_date
            FROM work_progress
            WHERE client_id = ?
            ORDER BY id DESC
        """, (client_id,))

        return self.cursor.fetchall()

    def get_notifications(self):
        self.cursor.execute("""
            SELECT
                id,
                message,
                status,
                created_date
            FROM notifications
            ORDER BY id DESC
        """)

        return self.cursor.fetchall()

    def mark_notification_read(self, notification_id):
        self.cursor.execute("""
            UPDATE notifications
            SET status = 'Read'
            WHERE id = ?
        """, (notification_id,))

        self.conn.commit()