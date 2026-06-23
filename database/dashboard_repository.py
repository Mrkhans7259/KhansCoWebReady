import sqlite3


class DashboardRepository:

    def __init__(self):
        self.conn = sqlite3.connect("khansco.db")
        self.cursor = self.conn.cursor()

    def total_clients(self):
        self.cursor.execute(
            "SELECT COUNT(*) FROM clients"
        )
        return self.cursor.fetchone()[0]

    def total_gst_records(self):
        self.cursor.execute(
            "SELECT COUNT(*) FROM gst_status"
        )
        return self.cursor.fetchone()[0]

    def pending_gstr1(self):
        self.cursor.execute("""
        SELECT COUNT(*)
        FROM gst_status
        WHERE gstr1_status != 'Filed'
        """)
        return self.cursor.fetchone()[0]

    def pending_gstr3b(self):
        self.cursor.execute("""
        SELECT COUNT(*)
        FROM gst_status
        WHERE gstr3b_status != 'Filed'
        """)
        return self.cursor.fetchone()[0]