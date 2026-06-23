import sqlite3
from datetime import datetime

DB_PATH = "khansco.db"


class FileCenterRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                file_title TEXT,
                file_name TEXT,
                file_type TEXT,
                uploaded_date TEXT
            )
        """)
        self.conn.commit()

    def get_clients(self):
        self.cursor.execute("""
            SELECT id, client_name
            FROM clients
            ORDER BY client_name
        """)
        return self.cursor.fetchall()

    def save_file(self, client_id, file_title, file_name, file_type):
        self.cursor.execute("""
            INSERT INTO client_files (
                client_id,
                file_title,
                file_name,
                file_type,
                uploaded_date
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            client_id,
            file_title,
            file_name,
            file_type,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ))
        self.conn.commit()

    def get_all_files(self):
        self.cursor.execute("""
            SELECT
                client_files.id,
                clients.client_name,
                client_files.file_title,
                client_files.file_name,
                client_files.file_type,
                client_files.uploaded_date
            FROM client_files
            JOIN clients ON client_files.client_id = clients.id
            ORDER BY client_files.id DESC
        """)
        return self.cursor.fetchall()

    def get_client_files(self, client_id):
        self.cursor.execute("""
            SELECT
                file_title,
                file_name,
                file_type,
                uploaded_date
            FROM client_files
            WHERE client_id = ?
            ORDER BY id DESC
        """, (client_id,))
        return self.cursor.fetchall()