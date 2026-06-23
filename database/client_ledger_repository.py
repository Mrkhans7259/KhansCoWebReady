import sqlite3

DB_PATH = "khansco.db"


class ClientLedgerRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def get_clients(self):
        self.cursor.execute("""
            SELECT id, client_name
            FROM clients
            ORDER BY client_name
        """)
        return self.cursor.fetchall()

    def get_ledger(self, client_id):
        self.cursor.execute("""
            SELECT
                financial_year,
                month,
                fee_amount,
                received_amount,
                balance_amount,
                payment_date,
                remarks
            FROM fee_tracker
            WHERE client_id = ?
            ORDER BY id DESC
        """, (client_id,))
        return self.cursor.fetchall()

    def get_summary(self, client_id):
        self.cursor.execute("""
            SELECT
                COALESCE(SUM(fee_amount), 0),
                COALESCE(SUM(received_amount), 0),
                COALESCE(SUM(balance_amount), 0)
            FROM fee_tracker
            WHERE client_id = ?
        """, (client_id,))
        return self.cursor.fetchone()