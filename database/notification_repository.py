import sqlite3

DB_PATH = "khansco.db"


class NotificationRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def unread_notifications_count(self):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM notifications
            WHERE status = 'Unread'
        """)
        return self.cursor.fetchone()[0]

    def open_tickets_count(self):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM tickets
            WHERE status != 'Closed'
        """)
        return self.cursor.fetchone()[0]

    def uploaded_documents_count(self):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM client_documents
        """)
        return self.cursor.fetchone()[0]

    def registered_clients_count(self):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM client_logins
        """)
        return self.cursor.fetchone()[0]