// frontend/src/api.js
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:5000"; // Flask backend

export async function addUser(userData) {
  const res = await axios.post(`${API_BASE_URL}/add_user`, userData);
  return res.data;
}

export async function getMatches(userId) {
  const res = await axios.get(`${API_BASE_URL}/get_matches`, {
    params: { user_id: userId },
  });
  return res.data;
}

export async function addSession(sessionData) {
  const res = await axios.post(`${API_BASE_URL}/add_session`, sessionData);
  return res.data;
}

export async function getProgress(userId) {
  const res = await axios.get(`${API_BASE_URL}/get_progress`, {
    params: { user_id: userId },
  });
  return res.data;
}
