import sqlite3

DB_PATH = "khansco.db"


class ReportRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def summary(self):
        self.cursor.execute("SELECT COUNT(*) FROM clients")
        total_clients = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM gst_status")
        total_gst = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM gst_status
            WHERE gstr1_status != 'Filed'
        """)
        pending_gstr1 = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM gst_status
            WHERE gstr3b_status != 'Filed'
        """)
        pending_gstr3b = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT
                COALESCE(SUM(fee_amount), 0),
                COALESCE(SUM(received_amount), 0),
                COALESCE(SUM(balance_amount), 0)
            FROM fee_tracker
        """)
        fee_summary = self.cursor.fetchone()

        self.cursor.execute("""
            SELECT
                COALESCE(SUM(total_amount), 0),
                COUNT(*)
            FROM invoices
        """)
        invoice_summary = self.cursor.fetchone()

        return {
            "total_clients": total_clients,
            "total_gst": total_gst,
            "pending_gstr1": pending_gstr1,
            "pending_gstr3b": pending_gstr3b,
            "total_fee": fee_summary[0],
            "received_fee": fee_summary[1],
            "outstanding_fee": fee_summary[2],
            "invoice_total": invoice_summary[0],
            "invoice_count": invoice_summary[1],
        }

    def outstanding_fees(self):
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

    def gst_pending(self):
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

    def invoice_report(self):
        self.cursor.execute("""
            SELECT
                invoices.invoice_no,
                invoices.invoice_date,
                clients.client_name,
                invoices.description,
                invoices.amount,
                invoices.gst_amount,
                invoices.total_amount
            FROM invoices
            JOIN clients ON invoices.client_id = clients.id
            ORDER BY invoices.id DESC
        """)
        return self.cursor.fetchall()