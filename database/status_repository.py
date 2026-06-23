import sqlite3
from datetime import datetime

DB_PATH = "khansco.db"


class StatusRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                gst_status TEXT,
                income_tax_status TEXT,
                tds_status TEXT,
                audit_status TEXT,
                roc_status TEXT,
                remarks TEXT,
                updated_date TEXT
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

    def save_status(
        self,
        client_id,
        gst_status,
        income_tax_status,
        tds_status,
        audit_status,
        roc_status,
        remarks
    ):
        self.cursor.execute("""
            SELECT id FROM client_status
            WHERE client_id = ?
        """, (client_id,))

        existing = self.cursor.fetchone()

        if existing:
            self.cursor.execute("""
                UPDATE client_status
                SET
                    gst_status = ?,
                    income_tax_status = ?,
                    tds_status = ?,
                    audit_status = ?,
                    roc_status = ?,
                    remarks = ?,
                    updated_date = ?
                WHERE client_id = ?
            """, (
                gst_status,
                income_tax_status,
                tds_status,
                audit_status,
                roc_status,
                remarks,
                datetime.now().strftime("%d-%m-%Y %H:%M"),
                client_id
            ))
        else:
            self.cursor.execute("""
                INSERT INTO client_status (
                    client_id,
                    gst_status,
                    income_tax_status,
                    tds_status,
                    audit_status,
                    roc_status,
                    remarks,
                    updated_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_id,
                gst_status,
                income_tax_status,
                tds_status,
                audit_status,
                roc_status,
                remarks,
                datetime.now().strftime("%d-%m-%Y %H:%M")
            ))

        self.conn.commit()

    def get_all_status(self):
        self.cursor.execute("""
            SELECT
                client_status.id,
                clients.client_name,
                client_status.gst_status,
                client_status.income_tax_status,
                client_status.tds_status,
                client_status.audit_status,
                client_status.roc_status,
                client_status.remarks,
                client_status.updated_date
            FROM client_status
            JOIN clients ON client_status.client_id = clients.id
            ORDER BY clients.client_name
        """)
        return self.cursor.fetchall()

    def get_client_status(self, client_id):
        self.cursor.execute("""
            SELECT
                gst_status,
                income_tax_status,
                tds_status,
                audit_status,
                roc_status,
                remarks,
                updated_date
            FROM client_status
            WHERE client_id = ?
        """, (client_id,))
        return self.cursor.fetchone()