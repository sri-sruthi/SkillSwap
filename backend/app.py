# backend/app.py
from flask_cors import CORS

from flask import Flask, request, jsonify
import sqlite3
import os
import json
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Path to the SQLite database file (inside backend folder)
DB_PATH = os.path.join(os.path.dirname(__file__), 'skillswap.db')


def get_db_connection():
    """
    Open a connection to the SQLite database.
    The row_factory makes query results behave like dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create the required tables if they don't exist:
    - users: stores user profile data
    - sessions: stores session logs between learner & teacher
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        skills_known TEXT,
        skills_want TEXT,
        location TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        teacher_id INTEGER,
        skill TEXT,
        session_notes TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()


# Create the Flask app
app = Flask(__name__)
CORS(app)


@app.route('/init_db', methods=['POST'])
def init_db_route():
    """
    Initialize the database tables. Call this once before adding data.
    """
    init_db()
    return jsonify({'status': 'ok', 'message': 'db initialized'})


@app.route('/add_user', methods=['POST'])
def add_user():
    """
    Add a user. Expects JSON body:
    {
      "name": "Anita",
      "skills_known": ["Python", "Excel"],
      "skills_want": ["SQL"],
      "location": "Chennai"
    }
    Returns created user_id.
    """
    data = request.get_json()
    name = data.get('name', '')
    skills_known = json.dumps(data.get('skills_known', []))  # store lists as JSON text
    skills_want = json.dumps(data.get('skills_want', []))
    location = data.get('location', '')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO users (name, skills_known, skills_want, location) VALUES (?,?,?,?)',
        (name, skills_known, skills_want, location)
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return jsonify({'status': 'ok', 'user_id': user_id})


@app.route('/users', methods=['GET'])
def get_all_users():
    """
    Debug route to see all users in the database.
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    user_list = []
    for row in users:
        user_list.append({
            'id': row['user_id'],
            'name': row['name'],
            'skills_known': row['skills_known'],
            'skills_want': row['skills_want'],
            'location': row['location']
        })
    return jsonify(user_list)


@app.route('/get_matches')
def get_matches():
    user_id = request.args.get('user_id', type=int)
    conn = get_db_connection()
    c = conn.cursor()
    users = c.execute('SELECT * FROM users').fetchall()
    conn.close()

    if not users:
        return jsonify([])

    user_list = []
    for row in users:
        user_list.append({
            'id': row['user_id'],
            'name': row['name'],
            'skills_known': row['skills_known'],
            'skills_want': row['skills_want'],
            'location': row['location']
        })

    current_user = next((u for u in user_list if u['id'] == user_id), None)
    if not current_user:
        return jsonify({'status': 'error', 'message': 'user not found'}), 404

    # Build text profiles for matching
    profiles = []
    for u in user_list:
        text = (u['skills_known'] or "") + " " + (u['skills_want'] or "")
        profiles.append(text)

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(profiles)

    # compute cosine similarity with current user
    user_index = user_list.index(current_user)
    cosine_similarities = cosine_similarity(tfidf_matrix[user_index], tfidf_matrix).flatten()

    # rank and select top 5
    similar_indices = cosine_similarities.argsort()[::-1][1:6]
    matches = [user_list[i] for i in similar_indices]

    return jsonify(matches)


@app.route('/add_session', methods=['POST'])
def add_session():
    """
    Log a learning session.
    JSON body:
    {
      "user_id": 1,
      "teacher_id": 2,
      "skill": "SQL",
      "session_notes": "Covered SELECT and WHERE"
    }
    """
    data = request.get_json()
    user_id = data.get('user_id')
    teacher_id = data.get('teacher_id')
    skill = data.get('skill', '')
    session_notes = data.get('session_notes', '')
    timestamp = datetime.utcnow().isoformat()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO sessions (user_id, teacher_id, skill, session_notes, timestamp) VALUES (?,?,?,?,?)',
        (user_id, teacher_id, skill, session_notes, timestamp)
    )
    conn.commit()
    session_id = cur.lastrowid
    conn.close()
    return jsonify({'status': 'ok', 'session_id': session_id})


@app.route('/get_progress', methods=['GET'])
def get_progress():
    """
    Returns session logs for a user (newest first).
    Provide ?user_id=1
    """
    user_id = request.args.get('user_id', type=int)
    if user_id is None:
        return jsonify({'status': 'error', 'message': 'user_id required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sessions WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
    sessions = cur.fetchall()
    out = []
    for s in sessions:
        out.append({
            'session_id': s['session_id'],
            'teacher_id': s['teacher_id'],
            'skill': s['skill'],
            'session_notes': s['session_notes'],
            'timestamp': s['timestamp']
        })
    conn.close()
    return jsonify(out)


# Run the app
if __name__ == '__main__':
    # If DB file doesn't exist, create tables
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, port=5000)
