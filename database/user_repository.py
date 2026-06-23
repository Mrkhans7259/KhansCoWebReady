import sqlite3
import hashlib

DB_PATH = "khansco.db"


class UserRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.create_table()
        self.create_default_admin()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        """)
        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_default_admin(self):
        self.cursor.execute(
            "SELECT COUNT(*) FROM users WHERE username = ?",
            ("admin",)
        )

        count = self.cursor.fetchone()[0]

        if count == 0:
            self.cursor.execute("""
                INSERT INTO users
                (
                    username,
                    password,
                    role
                )
                VALUES (?, ?, ?)
            """, (
                "admin",
                self.hash_password("admin123"),
                "Admin"
            ))

            self.conn.commit()

    def verify_login(self, username, password):

        hashed_password = self.hash_password(password)

        self.cursor.execute("""
            SELECT
                id,
                username,
                role
            FROM users
            WHERE username = ?
            AND password = ?
        """, (
            username,
            hashed_password
        ))

        return self.cursor.fetchone()

    def get_all_users(self):

        self.cursor.execute("""
            SELECT
                id,
                username,
                role
            FROM users
            ORDER BY username
        """)

        return self.cursor.fetchall()

    def get_user_by_id(self, user_id):

        self.cursor.execute("""
            SELECT
                id,
                username,
                role
            FROM users
            WHERE id = ?
        """, (user_id,))

        return self.cursor.fetchone()

    def add_user(self, username, password, role):

        self.cursor.execute("""
            INSERT INTO users
            (
                username,
                password,
                role
            )
            VALUES (?, ?, ?)
        """, (
            username,
            self.hash_password(password),
            role
        ))

        self.conn.commit()

    def update_user(
        self,
        user_id,
        username,
        password,
        role
    ):

        if password:

            self.cursor.execute("""
                UPDATE users
                SET
                    username = ?,
                    password = ?,
                    role = ?
                WHERE id = ?
            """, (
                username,
                self.hash_password(password),
                role,
                user_id
            ))

        else:

            self.cursor.execute("""
                UPDATE users
                SET
                    username = ?,
                    role = ?
                WHERE id = ?
            """, (
                username,
                role,
                user_id
            ))

        self.conn.commit()

    def delete_user(self, user_id):

        self.cursor.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )

        self.conn.commit()