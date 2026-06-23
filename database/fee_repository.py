import sqlite3

DB_PATH = "khansco.db"


class FeeRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fee_tracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                financial_year TEXT,
                month TEXT,
                fee_amount REAL,
                received_amount REAL,
                balance_amount REAL,
                payment_date TEXT,
                remarks TEXT
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

    def add_fee(self, client_id, financial_year, month, fee_amount, received_amount, payment_date, remarks):
        fee_amount = float(fee_amount or 0)
        received_amount = float(received_amount or 0)
        balance_amount = fee_amount - received_amount

        self.cursor.execute("""
            INSERT INTO fee_tracker (
                client_id, financial_year, month, fee_amount,
                received_amount, balance_amount, payment_date, remarks
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id, financial_year, month, fee_amount,
            received_amount, balance_amount, payment_date, remarks
        ))
        self.conn.commit()

    def get_all_fees(self):
        self.cursor.execute("""
            SELECT
                fee_tracker.id,
                clients.client_name,
                fee_tracker.financial_year,
                fee_tracker.month,
                fee_tracker.fee_amount,
                fee_tracker.received_amount,
                fee_tracker.balance_amount,
                fee_tracker.payment_date,
                fee_tracker.remarks
            FROM fee_tracker
            JOIN clients ON fee_tracker.client_id = clients.id
            ORDER BY fee_tracker.id DESC
        """)
        return self.cursor.fetchall()

    def totals(self):
        self.cursor.execute("""
            SELECT
                COALESCE(SUM(fee_amount), 0),
                COALESCE(SUM(received_amount), 0),
                COALESCE(SUM(balance_amount), 0)
            FROM fee_tracker
        """)
        return self.cursor.fetchone()