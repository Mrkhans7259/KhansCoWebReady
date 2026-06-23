import sqlite3
from datetime import datetime

DB_PATH = "khansco.db"


class InvoiceRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT,
                invoice_date TEXT,
                client_id INTEGER,
                description TEXT,
                amount REAL,
                gst_rate REAL,
                gst_amount REAL,
                total_amount REAL
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

    def next_invoice_no(self):
        self.cursor.execute("SELECT COUNT(*) FROM invoices")
        count = self.cursor.fetchone()[0] + 1
        year = datetime.now().strftime("%Y")
        return f"KH/{year}/{count:04d}"

    def add_invoice(self, invoice_no, invoice_date, client_id, description, amount, gst_rate):
        amount = float(amount or 0)
        gst_rate = float(gst_rate or 0)
        gst_amount = amount * gst_rate / 100
        total_amount = amount + gst_amount

        self.cursor.execute("""
            INSERT INTO invoices (
                invoice_no, invoice_date, client_id, description,
                amount, gst_rate, gst_amount, total_amount
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_no, invoice_date, client_id, description,
            amount, gst_rate, gst_amount, total_amount
        ))
        self.conn.commit()

    def get_all_invoices(self):
        self.cursor.execute("""
            SELECT
                invoices.id,
                invoices.invoice_no,
                invoices.invoice_date,
                clients.client_name,
                invoices.description,
                invoices.amount,
                invoices.gst_rate,
                invoices.gst_amount,
                invoices.total_amount
            FROM invoices
            JOIN clients ON invoices.client_id = clients.id
            ORDER BY invoices.id DESC
        """)
        return self.cursor.fetchall()