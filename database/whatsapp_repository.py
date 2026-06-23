import sqlite3

DB_PATH = "khansco.db"


class WhatsAppRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def get_clients(self):
        self.cursor.execute("""
            SELECT
                id,
                client_name,
                mobile
            FROM clients
            WHERE mobile IS NOT NULL
            AND mobile != ''
            ORDER BY client_name
        """)
        return self.cursor.fetchall()

    def gst_pending_clients(self):
        self.cursor.execute("""
            SELECT
                clients.client_name,
                clients.mobile,
                gst_status.financial_year,
                gst_status.month,
                gst_status.gstr1_status,
                gst_status.gstr3b_status
            FROM gst_status
            JOIN clients ON gst_status.client_id = clients.id
            WHERE gst_status.gstr1_status != 'Filed'
               OR gst_status.gstr3b_status != 'Filed'
            ORDER BY clients.client_name
        """)
        return self.cursor.fetchall()

    def fee_pending_clients(self):
        self.cursor.execute("""
            SELECT
                clients.client_name,
                clients.mobile,
                fee_tracker.financial_year,
                fee_tracker.month,
                fee_tracker.balance_amount
            FROM fee_tracker
            JOIN clients ON fee_tracker.client_id = clients.id
            WHERE fee_tracker.balance_amount > 0
            ORDER BY fee_tracker.balance_amount DESC
        """)
        return self.cursor.fetchall()