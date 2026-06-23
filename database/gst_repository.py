import sqlite3

DB_PATH = "khansco.db"


class GSTRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS gst_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                financial_year TEXT,
                month TEXT,
                gstr1_status TEXT,
                gstr3b_status TEXT,
                arn TEXT,
                filing_date TEXT
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

    def add_gst_status(
        self,
        client_id,
        financial_year,
        month,
        gstr1_status,
        gstr3b_status,
        arn,
        filing_date
    ):
        self.cursor.execute("""
            INSERT INTO gst_status (
                client_id,
                financial_year,
                month,
                gstr1_status,
                gstr3b_status,
                arn,
                filing_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id,
            financial_year,
            month,
            gstr1_status,
            gstr3b_status,
            arn,
            filing_date
        ))
        self.conn.commit()

    def get_all_gst_status(self):
        self.cursor.execute("""
            SELECT
                gst_status.id,
                clients.client_name,
                gst_status.financial_year,
                gst_status.month,
                gst_status.gstr1_status,
                gst_status.gstr3b_status,
                gst_status.arn,
                gst_status.filing_date
            FROM gst_status
            JOIN clients ON gst_status.client_id = clients.id
            ORDER BY gst_status.id DESC
        """)
        return self.cursor.fetchall()

    def search_gst_status(self, search_text):
        self.cursor.execute("""
            SELECT
                gst_status.id,
                clients.client_name,
                gst_status.financial_year,
                gst_status.month,
                gst_status.gstr1_status,
                gst_status.gstr3b_status,
                gst_status.arn,
                gst_status.filing_date
            FROM gst_status
            JOIN clients ON gst_status.client_id = clients.id
            WHERE
                clients.client_name LIKE ?
                OR gst_status.month LIKE ?
                OR gst_status.financial_year LIKE ?
                OR gst_status.gstr1_status LIKE ?
                OR gst_status.gstr3b_status LIKE ?
            ORDER BY gst_status.id DESC
        """, (
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%"
        ))
        return self.cursor.fetchall()

    def delete_gst_status(self, gst_id):
        self.cursor.execute(
            "DELETE FROM gst_status WHERE id = ?",
            (gst_id,)
        )
        self.conn.commit()