import sqlite3

DB_PATH = "khansco.db"


class ProfileRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def get_client_profile(self, client_id):
        self.cursor.execute("""
            SELECT
                id,
                client_code,
                client_name,
                gstin,
                mobile,
                email,
                assigned_staff
            FROM clients
            WHERE id = ?
        """, (client_id,))
        return self.cursor.fetchone()

    def update_client_profile(
        self,
        client_id,
        client_code,
        client_name,
        gstin,
        mobile,
        email,
        assigned_staff
    ):
        self.cursor.execute("""
            UPDATE clients
            SET
                client_code = ?,
                client_name = ?,
                gstin = ?,
                mobile = ?,
                email = ?,
                assigned_staff = ?
            WHERE id = ?
        """, (
            client_code,
            client_name,
            gstin,
            mobile,
            email,
            assigned_staff,
            client_id
        ))
        self.conn.commit()

    def get_outstanding_fee(self, client_id):
        self.cursor.execute("""
            SELECT COALESCE(SUM(balance_amount), 0)
            FROM fee_tracker
            WHERE client_id = ?
        """, (client_id,))
        return self.cursor.fetchone()[0]