import sqlite3
import csv
import os

DB_PATH = "khansco.db"


class BackupRepository:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def export_table_to_csv(self, table_name, file_path):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()

        columns = [description[0] for description in self.cursor.description]

        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            writer.writerows(rows)

        return file_path

    def database_exists(self):
        return os.path.exists(DB_PATH)