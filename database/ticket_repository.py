import sqlite3
from datetime import datetime

DB_PATH = "khansco.db"


class TicketRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                subject TEXT,
                message TEXT,
                status TEXT,
                created_date TEXT
            )
        """)
        self.conn.commit()

    def create_ticket(self, client_id, subject, message):
        self.cursor.execute("""
            INSERT INTO tickets (
                client_id,
                subject,
                message,
                status,
                created_date
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            client_id,
            subject,
            message,
            "Open",
            datetime.now().strftime("%d-%m-%Y %H:%M")
        ))
        self.conn.commit()

    def get_client_tickets(self, client_id):
        self.cursor.execute("""
            SELECT id, subject, message, status, created_date
            FROM tickets
            WHERE client_id = ?
            ORDER BY id DESC
        """, (client_id,))
        return self.cursor.fetchall()

    def get_all_tickets(self):
        self.cursor.execute("""
            SELECT
                tickets.id,
                clients.client_name,
                tickets.subject,
                tickets.message,
                tickets.status,
                tickets.created_date
            FROM tickets
            JOIN clients ON tickets.client_id = clients.id
            ORDER BY tickets.id DESC
        """)
        return self.cursor.fetchall()

    def update_status(self, ticket_id, status):
        self.cursor.execute("""
            UPDATE tickets
            SET status = ?
            WHERE id = ?
        """, (status, ticket_id))
        self.conn.commit()