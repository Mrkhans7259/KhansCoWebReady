import sqlite3

DB_PATH = "khansco.db"


class ClientRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def get_all_clients(self):
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
            ORDER BY client_name
        """)
        return self.cursor.fetchall()

    def search_clients(self, search_text):
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
            WHERE
                client_name LIKE ?
                OR gstin LIKE ?
                OR mobile LIKE ?
                OR client_code LIKE ?
            ORDER BY client_name
        """, (
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%"
        ))

        return self.cursor.fetchall()

    def get_client_by_id(self, client_id):
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

    def add_client(
        self,
        client_code,
        client_name,
        gstin,
        mobile,
        email,
        assigned_staff
    ):
        self.cursor.execute("""
            INSERT INTO clients
            (
                client_code,
                client_name,
                gstin,
                mobile,
                email,
                assigned_staff
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            client_code,
            client_name,
            gstin,
            mobile,
            email,
            assigned_staff
        ))

        self.conn.commit()

    def update_client(
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

    def delete_client(self, client_id):
        self.cursor.execute(
            "DELETE FROM clients WHERE id = ?",
            (client_id,)
        )
        self.conn.commit()