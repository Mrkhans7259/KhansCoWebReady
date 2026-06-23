from database.db_connection import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(100),
    role VARCHAR(50)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    client_code VARCHAR(50),
    client_name VARCHAR(200),
    gstin VARCHAR(50),
    mobile VARCHAR(50),
    email VARCHAR(200),
    assigned_staff VARCHAR(100)
);
""")

conn.commit()

print("PostgreSQL tables created successfully")

cur.close()
conn.close()