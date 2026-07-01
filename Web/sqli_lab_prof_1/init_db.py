import sqlite3

conn = sqlite3.connect("database.db")

c = conn.cursor()

c.execute("""
CREATE TABLE users(
id INTEGER PRIMARY KEY,
username TEXT,
password TEXT
)
""")

c.execute("""
INSERT INTO users(username,password)
VALUES
('admin','SuperSecret123')
""")

conn.commit()

conn.close()
