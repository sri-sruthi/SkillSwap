// frontend/src/api.js
import axios from "axios";

// Flask backend base URL
const API_BASE_URL = "http://127.0.0.1:5000";

// Add a new user
export async function addUser(userData) {
  const res = await axios.post(`${API_BASE_URL}/add_user`, userData);
  return res.data;
}

// Get skill swap matches for a given user
export async function getMatches(userId) {
  const res = await axios.get(`${API_BASE_URL}/get_matches`, {
    params: { user_id: userId },
  });
  return res.data;
}

// Log a learning session
export async function addSession(sessionData) {
  const res = await axios.post(`${API_BASE_URL}/add_session`, sessionData);
  return res.data;
}

// Get progress (past sessions) for a user
export async function getProgress(userId) {
  const res = await axios.get(`${API_BASE_URL}/get_progress`, {
    params: { user_id: userId },
  });
  return res.data;
}

// Get top skills being taught and learned (Skill Trends)
export async function getTopSkills() {
  const res = await axios.get(`${API_BASE_URL}/top_skills`);
  return res.data;
}
