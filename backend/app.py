from flask_cors import CORS
from flask import Flask, request, jsonify
import sqlite3
import os
import json
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

# Optional: For AI summarizer
try:
    from transformers import pipeline
    summarizer = pipeline("summarization", model="t5-small")
except Exception:
    summarizer = None

# Path to the SQLite database file (inside backend folder)
DB_PATH = os.path.join(os.path.dirname(__file__), 'skillswap.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
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

    # Avoid duplicate entries
    cur.execute("SELECT user_id FROM users WHERE name = ? AND location = ?", (name, location))
    existing = cur.fetchone()
    if existing:
        conn.close()
        return jsonify({'status': 'exists', 'user_id': existing['user_id'], 'message': 'User already exists.'})

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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    user_list = [{
        'id': row['user_id'],
        'name': row['name'],
        'skills_known': row['skills_known'],
        'skills_want': row['skills_want'],
        'location': row['location']
    } for row in users]
    return jsonify(user_list)


# ✅ AI-Enhanced Hybrid Matching
@app.route('/get_matches')
def get_matches():
    """
    AI-enhanced hybrid matching:
    Combines logical overlap + semantic similarity (TF-IDF cosine)
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'status': 'error', 'message': 'user_id required'}), 400

    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    if not users:
        return jsonify([])

    user_list = []
    for row in users:
        try:
            skills_known = json.loads(row['skills_known'])
            skills_want = json.loads(row['skills_want'])
        except (json.JSONDecodeError, TypeError):
            skills_known = [row['skills_known']] if row['skills_known'] else []
            skills_want = [row['skills_want']] if row['skills_want'] else []
        user_list.append({
            'id': row['user_id'],
            'name': row['name'],
            'skills_known': skills_known,
            'skills_want': skills_want,
            'location': row['location']
        })

    current_user = next((u for u in user_list if u['id'] == user_id), None)
    if not current_user:
        return jsonify({'status': 'error', 'message': 'user not found'}), 404

    profiles = [" ".join(u['skills_known'] + u['skills_want']) for u in user_list]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(profiles)
    cosine_similarities = cosine_similarity(tfidf_matrix)
    user_index = next(i for i, u in enumerate(user_list) if u['id'] == user_id)

    matches = []
    for i, u in enumerate(user_list):
        if u['id'] == user_id:
            continue
        teaches_you = list(set(u['skills_known']) & set(current_user['skills_want']))
        learns_from_you = list(set(u['skills_want']) & set(current_user['skills_known']))
        overlap_score = len(teaches_you) + len(learns_from_you)
        semantic_score = cosine_similarities[user_index][i]
        final_score = round((0.6 * semantic_score) + (0.4 * overlap_score), 3)

        if final_score > 0:
            matches.append({
                'id': u['id'],
                'name': u['name'],
                'location': u['location'],
                'skills_they_can_teach': teaches_you,
                'skills_you_can_teach': learns_from_you,
                'semantic_score': round(semantic_score, 3),
                'overlap_score': overlap_score,
                'match_score': final_score
            })

    matches = sorted(matches, key=lambda x: x['match_score'], reverse=True)
    return jsonify(matches)


# ✅ AI Skill Recommendation System
@app.route('/ai_suggest_skills')
def ai_suggest_skills():
    """
    Suggest new skills for a user to learn based on similar users' skill patterns (TF-IDF similarity)
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'status': 'error', 'message': 'user_id required'}), 400

    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    user_list = []
    for row in users:
        user_list.append({
            'id': row['user_id'],
            'name': row['name'],
            'skills_known': json.loads(row['skills_known']),
            'skills_want': json.loads(row['skills_want'])
        })

    current_user = next((u for u in user_list if u['id'] == user_id), None)
    if not current_user:
        return jsonify({'status': 'error', 'message': 'user not found'}), 404

    profiles = [" ".join(u['skills_known'] + u['skills_want']) for u in user_list]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(profiles)
    cosine_similarities = cosine_similarity(tfidf_matrix)
    user_index = user_list.index(current_user)
    similarities = cosine_similarities[user_index]

    similar_users = sorted(
        [(user_list[i], similarities[i]) for i in range(len(user_list)) if i != user_index],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    suggested_skills = set()
    for u, score in similar_users:
        for skill in u['skills_want']:
            if skill not in current_user['skills_known'] and skill not in current_user['skills_want']:
                suggested_skills.add(skill)

    return jsonify({
        'user': current_user['name'],
        'suggested_skills': list(suggested_skills)[:5],
        'message': "AI-generated recommendations using TF-IDF user similarity."
    })


# ✅ AI Session Summarizer
@app.route('/summarize_session', methods=['POST'])
def summarize_session():
    data = request.get_json()
    text = data.get("session_notes", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    if summarizer is None:
        return jsonify({"error": "Summarizer not available. Install transformers."}), 500
    summary = summarizer(text, max_length=40, min_length=10, do_sample=False)
    return jsonify({"summary": summary[0]["summary_text"]})


@app.route('/add_session', methods=['POST'])
def add_session():
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
    user_id = request.args.get('user_id', type=int)
    if user_id is None:
        return jsonify({'status': 'error', 'message': 'user_id required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sessions WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
    sessions = cur.fetchall()
    out = [{
        'session_id': s['session_id'],
        'teacher_id': s['teacher_id'],
        'skill': s['skill'],
        'session_notes': s['session_notes'],
        'timestamp': s['timestamp']
    } for s in sessions]
    conn.close()
    return jsonify(out)


@app.route('/user_summary', methods=['GET'])
def user_summary():
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

    summaries = [{
        "id": r["user_id"],
        "name": r["name"],
        "location": r["location"],
        "total_sessions": r["total_sessions"],
        "last_session": r["last_session"]
    } for r in rows]
    return jsonify(summaries)


@app.route('/top_skills')
def top_skills():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT skills_known, skills_want FROM users")
    rows = cur.fetchall()
    teach_skills, learn_skills = [], []

    for row in rows:
        try:
            teach_skills.extend(json.loads(row['skills_known']))
            learn_skills.extend(json.loads(row['skills_want']))
        except:
            pass

    top_teach = [{"skill": s, "count": c} for s, c in Counter(teach_skills).most_common(5)]
    top_learn = [{"skill": s, "count": c} for s, c in Counter(learn_skills).most_common(5)]
    conn.close()
    return jsonify({"top_teach": top_teach, "top_learn": top_learn})


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, port=5000)