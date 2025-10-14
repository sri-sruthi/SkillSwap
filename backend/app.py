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
    data = request.get_json()
    name = data.get('name', '')
    skills_known = json.dumps(data.get('skills_known', []))
    skills_want = json.dumps(data.get('skills_want', []))
    location = data.get('location', '')

    conn = get_db_connection()
    cur = conn.cursor()

    # 🧠 Check if a user with the same name and location exists
    cur.execute("SELECT user_id FROM users WHERE name = ? AND location = ?", (name, location))
    existing = cur.fetchone()

    if existing:
        user_id = existing['user_id']
        conn.close()
        return jsonify({'status': 'exists', 'user_id': user_id, 'message': 'User already exists.'})

    # Otherwise insert new
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
    """
    Finds users who are a good match based on complementary skills:
    - Someone who can teach what the current user wants to learn
    - Someone who wants to learn what the current user can teach
    """

    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'status': 'error', 'message': 'user_id required'}), 400

    conn = get_db_connection()
    c = conn.cursor()
    users = c.execute('SELECT * FROM users').fetchall()
    conn.close()

    if not users:
        return jsonify([])

    # Build user list
    user_list = []
    for row in users:
        user_list.append({
            'id': row['user_id'],
            'name': row['name'],
            'skills_known': json.loads(row['skills_known']),
            'skills_want': json.loads(row['skills_want']),
            'location': row['location']
        })

    # Find the current user
    current_user = next((u for u in user_list if u['id'] == user_id), None)
    if not current_user:
        return jsonify({'status': 'error', 'message': 'user not found'}), 404

    matches = []

    # Compare current user with all others
    for u in user_list:
        if u['id'] == current_user['id']:
            continue

        # Skills overlap calculations
        teaches_you = list(set(u['skills_known']) & set(current_user['skills_want']))
        learns_from_you = list(set(u['skills_want']) & set(current_user['skills_known']))
        mutual_score = len(teaches_you) + len(learns_from_you)

        # Include if at least one meaningful overlap exists
        if mutual_score > 0:
            matches.append({
                'id': u['id'],
                'name': u['name'],
                'location': u['location'],
                'skills_they_can_teach': teaches_you,
                'skills_you_can_teach': learns_from_you,
                'match_score': mutual_score
            })

    # Sort matches by mutual score
    matches = sorted(matches, key=lambda x: x['match_score'], reverse=True)

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

@app.route('/user_summary', methods=['GET'])
def user_summary():
    """Returns total sessions and last session time for all users"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.user_id, u.name, u.location,
               COUNT(s.session_id) AS total_sessions,
               MAX(s.timestamp) AS last_session
        FROM users u
        LEFT JOIN sessions s ON u.user_id = s.user_id
        GROUP BY u.user_id
        ORDER BY u.name
    """)
    rows = cur.fetchall()
    conn.close()

    summaries = []
    for r in rows:
        summaries.append({
            "id": r["user_id"],
            "name": r["name"],
            "location": r["location"],
            "total_sessions": r["total_sessions"],
            "last_session": r["last_session"]
        })
    return jsonify(summaries)

@app.route('/top_skills')
def top_skills():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get all skills_known and skills_want to parse manually
    cur.execute("SELECT skills_known, skills_want FROM users")
    rows = cur.fetchall()
    
    teach_skills = []
    learn_skills = []
    
    for row in rows:
        # Parse skills_known
        try:
            skills_known = json.loads(row['skills_known'])
            if isinstance(skills_known, list):
                teach_skills.extend(skills_known)
        except (json.JSONDecodeError, TypeError):
            # If JSON parsing fails, try to handle as comma-separated string
            skills_str = row['skills_known']
            if skills_str and isinstance(skills_str, str):
                # Remove brackets and quotes if present, then split by comma
                cleaned = skills_str.strip('[]"\'')
                skills_list = [s.strip() for s in cleaned.split(',') if s.strip()]
                teach_skills.extend(skills_list)
        
        # Parse skills_want
        try:
            skills_want = json.loads(row['skills_want'])
            if isinstance(skills_want, list):
                learn_skills.extend(skills_want)
        except (json.JSONDecodeError, TypeError):
            # If JSON parsing fails, try to handle as comma-separated string
            skills_str = row['skills_want']
            if skills_str and isinstance(skills_str, str):
                # Remove brackets and quotes if present, then split by comma
                cleaned = skills_str.strip('[]"\'')
                skills_list = [s.strip() for s in cleaned.split(',') if s.strip()]
                learn_skills.extend(skills_list)
    
    # Count skills
    from collections import Counter
    top_teach = [{"skill": skill, "count": count} for skill, count in Counter(teach_skills).most_common(5)]
    top_learn = [{"skill": skill, "count": count} for skill, count in Counter(learn_skills).most_common(5)]
    
    conn.close()
    return jsonify({"top_teach": top_teach, "top_learn": top_learn})

# Run the app
if __name__ == '__main__':
    # If DB file doesn't exist, create tables
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, port=5000)
