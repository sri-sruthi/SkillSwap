# backend/sample_data.py
import sqlite3, os, json
DB_PATH = os.path.join(os.path.dirname(__file__), 'skillswap.db')

def insert_sample():
    conn = sqlite3.connect('skill_swap.db')
    conn.row_factory = sqlite3.Row  # ✅ allows accessing columns by name
    c = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            skills_known TEXT,
            skills_want TEXT,
            location TEXT
        )
    ''')
    users = [
        ("Anita", json.dumps(["Python", "Excel"]), json.dumps(["SQL", "Machine Learning"]), "Chennai"),
        ("Ravi", json.dumps(["SQL", "Python"]), json.dumps(["Excel"]), "Coimbatore"),
        ("Priya", json.dumps(["Machine Learning", "Python"]), json.dumps(["Data Visualization"]), "Madurai"),
        ("Asha", json.dumps(["Excel", "Public Speaking"]), json.dumps(["Python"]), "Tirunelveli"),
    ]
    for u in users:
        cur.execute('INSERT INTO users (name, skills_known, skills_want, location) VALUES (?,?,?,?)', u)
    conn.commit()
    conn.close()
    print("Inserted sample users")

if __name__ == '__main__':
    insert_sample()
