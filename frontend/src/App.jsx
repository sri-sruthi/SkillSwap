import { useState, useEffect } from "react";
import { motion } from "framer-motion";

const API_BASE_URL = "http://127.0.0.1:5000";

function App() {
  const [userId, setUserId] = useState(null);
  const [users, setUsers] = useState([]);
  const [matches, setMatches] = useState([]);
  const [progress, setProgress] = useState([]);
  const [topSkills, setTopSkills] = useState({ top_teach: [], top_learn: [] });
  const [summaries, setSummaries] = useState([]);

  // fetch all data on load
  useEffect(() => {
    fetchUsers();
    fetchTopSkills();
    fetchSummaries();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/users`);
      const data = await res.json();
      console.log("Users Response:", data);
      setUsers(data);
    } catch (err) {
      console.error("Error fetching users:", err);
    }
  };

  const fetchTopSkills = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/top_skills`);
      const data = await res.json();
      console.log("Top Skills Response:", data);
      setTopSkills(data || { top_teach: [], top_learn: [] });
    } catch (err) {
      console.error("Error fetching top skills:", err);
      setTopSkills({ top_teach: [], top_learn: [] });
    }
  };

  const fetchSummaries = async () => {
    const res = await fetch(`${API_BASE_URL}/user_summary`);
    const data = await res.json();
    setSummaries(data);
  };

  const handleAddUser = async () => {
    const name = prompt("Enter your name:");
    const skillsKnown = prompt("Enter skills you can teach (comma-separated):");
    const skillsWant = prompt("Enter skills you want to learn (comma-separated):");
    const location = prompt("Enter your location:");

    const user = {
      name,
      skills_known: skillsKnown.split(",").map((s) => s.trim()),
      skills_want: skillsWant.split(",").map((s) => s.trim()),
      location,
    };

    try {
      const res = await fetch(`${API_BASE_URL}/add_user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user)
      });
      const data = await res.json();
      setUserId(data.user_id);
      alert(`User added successfully! ID: ${data.user_id}`);
      fetchUsers();
      fetchTopSkills();
    } catch (error) {
      console.error("Error adding user:", error);
      alert("Failed to add user. Check the console for details.");
    }
  };

  const handleGetMatches = async () => {
    if (!userId) return alert("Select a user first!");
    try {
      const res = await fetch(`${API_BASE_URL}/get_matches?user_id=${userId}`);
      const data = await res.json();
      setMatches(data);
    } catch (err) {
      console.error("Error fetching matches:", err);
      alert("❌ Failed to fetch matches.");
    }
  };

  const handleAddSession = async () => {
    if (!userId) return alert("Select a user first!");
    const skill = prompt("Enter the skill you practiced or learned:");
    const session_notes = prompt("Enter brief session notes (e.g., topics covered):");
    if (!skill || !session_notes) {
      alert("Please provide both skill and session notes.");
      return;
    }

    const sessionData = {
      user_id: userId,
      teacher_id: 2,
      skill,
      session_notes,
    };

    try {
      await fetch(`${API_BASE_URL}/add_session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sessionData)
      });
      alert("✅ Session added!");
      fetchSummaries();
    } catch (err) {
      console.error("Error adding session:", err);
      alert("❌ Failed to add session.");
    }
  };

  const handleGetProgress = async () => {
    if (!userId) return alert("Select a user first!");
    try {
      const res = await fetch(`${API_BASE_URL}/get_progress?user_id=${userId}`);
      const data = await res.json();
      setProgress(data);
    } catch (err) {
      console.error("Error fetching progress:", err);
      alert("❌ Failed to fetch progress.");
    }
  };

  return (
    <div
      style={{
        padding: "2rem",
        fontFamily: "Inter, sans-serif",
        backgroundColor: "#f8f9fa",
        minHeight: "100vh",
      }}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        style={{ textAlign: "center", marginBottom: "2rem" }}
      >
        <h1 style={{ fontSize: "2.5rem", color: "#333", marginBottom: "0.3rem" }}>
          SkillSwap
        </h1>
        <p style={{ fontSize: "1.1rem", color: "#555" }}>
          Learn. Teach. Grow together through shared knowledge.
        </p>
      </motion.div>

      {/* Controls */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "1rem",
          marginBottom: "2rem",
          flexWrap: "wrap",
        }}
      >
        <select
          value={userId || ""}
          onChange={(e) => setUserId(Number(e.target.value))}
          style={{
            padding: "0.6rem",
            borderRadius: "6px",
            border: "1px solid #ccc",
            fontSize: "1rem",
          }}
        >
          <option value="">-- Choose User --</option>
          {users.map((u) => (
            <option key={u.id} value={u.id}>
              {u.name} ({u.location})
            </option>
          ))}
        </select>

        <button onClick={handleAddUser} style={buttonStyle}>Add User</button>
        <button onClick={handleGetMatches} style={buttonStyle}>Get Matches</button>
        <button onClick={handleAddSession} style={buttonStyle}>Add Session</button>
        <button onClick={handleGetProgress} style={buttonStyle}>Get Progress</button>
      </div>

      {/* Skill Trends */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
        style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "1.5rem",
          boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
          marginBottom: "2rem",
          maxWidth: "750px",
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        <h2 style={{ textAlign: "center", color: "#333" }}>Skill Trends</h2>
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "1rem", gap: "1rem", flexWrap: "wrap" }}>
          {/* Teaching */}
          <div style={{ flex: 1, minWidth: "250px" }}>
            <h3 style={{ color: "#007bff" }}>Top Skills Being Taught</h3>
            <ul style={{ paddingLeft: 0 }}>
              {topSkills.top_teach && topSkills.top_teach.length > 0 ? (
                topSkills.top_teach.map((s, index) => (
                  <li
                    key={index}
                    style={{
                      backgroundColor: "#e3f2fd",
                      margin: "8px 0",
                      padding: "6px 10px",
                      borderRadius: "6px",
                      listStyle: "none",
                      color: "#0d47a1",
                      fontWeight: "500",
                    }}
                  >
                    {s.skill} ({s.count})
                  </li>
                ))
              ) : (
                <p style={{ color: "#666", fontStyle: "italic" }}>No data yet. Add users to see trends!</p>
              )}
            </ul>
          </div>

          {/* Learning */}
          <div style={{ flex: 1, minWidth: "250px" }}>
            <h3 style={{ color: "#28a745" }}>Top Skills Being Learned</h3>
            <ul style={{ paddingLeft: 0 }}>
              {topSkills.top_learn && topSkills.top_learn.length > 0 ? (
                topSkills.top_learn.map((s, index) => (
                  <li
                    key={index}
                    style={{
                      backgroundColor: "#e8f5e9",
                      margin: "8px 0",
                      padding: "6px 10px",
                      borderRadius: "6px",
                      listStyle: "none",
                      color: "#1b5e20",
                      fontWeight: "500",
                    }}
                  >
                    {s.skill} ({s.count})
                  </li>
                ))
              ) : (
                <p style={{ color: "#666", fontStyle: "italic" }}>No data yet. Add users to see trends!</p>
              )}
            </ul>
          </div>
        </div>
      </motion.div>

      {/* User Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.2 }}
        style={{
          backgroundColor: "white",
          borderRadius: "12px",
          padding: "1.5rem",
          boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
          marginBottom: "2rem",
          maxWidth: "750px",
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        <h2 style={{ textAlign: "center", color: "#333" }}>User Summary</h2>
        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              marginTop: "1rem",
            }}
          >
            <thead>
              <tr style={{ backgroundColor: "#f0f0f0", textAlign: "left" }}>
                <th style={{ padding: "8px" }}>Name</th>
                <th style={{ padding: "8px" }}>Location</th>
                <th style={{ padding: "8px" }}>Sessions</th>
                <th style={{ padding: "8px" }}>Last Session</th>
              </tr>
            </thead>
            <tbody>
              {summaries.map((s) => (
                <tr key={s.id}>
                  <td style={{ padding: "8px" }}>{s.name}</td>
                  <td style={{ padding: "8px" }}>{s.location}</td>
                  <td style={{ padding: "8px" }}>{s.total_sessions}</td>
                  <td style={{ padding: "8px" }}>
                    {s.last_session ? new Date(s.last_session).toLocaleString() : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Matches & Progress */}
      <div style={{ maxWidth: "700px", margin: "auto" }}>
        <h2>Matches</h2>
        {matches.length > 0 ? (
          <ul style={{ listStyle: "none", paddingLeft: 0 }}>
            {matches.map((m, idx) => (
              <li key={idx} style={{ 
                marginBottom: "1rem", 
                backgroundColor: "white", 
                padding: "1rem", 
                borderRadius: "8px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
              }}>
                <strong>{m.name}</strong> ({m.location}) - Match Score: {m.match_score}
                <br />
                <span style={{ color: "#007bff" }}>
                  Can teach you: {m.skills_they_can_teach.join(", ") || "None"}
                </span>
                <br />
                <span style={{ color: "#28a745" }}>
                  You can teach: {m.skills_you_can_teach.join(", ") || "None"}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p>No matches yet. Select a user and click "Get Matches".</p>
        )}

        <h2 style={{ marginTop: "2rem" }}>Progress</h2>
        {progress.length > 0 ? (
          <ul style={{ listStyle: "none", paddingLeft: 0 }}>
            {progress.map((p) => (
              <li key={p.session_id} style={{ 
                marginBottom: "0.5rem",
                backgroundColor: "white",
                padding: "0.75rem",
                borderRadius: "6px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
              }}>
                <strong>{p.skill}</strong> → {p.session_notes} 
                <br />
                <span style={{ fontSize: "0.85rem", color: "#666" }}>
                  {new Date(p.timestamp).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p>No progress to display. Select a user and click "Get Progress".</p>
        )}
      </div>
    </div>
  );
}

const buttonStyle = {
  padding: "0.6rem 1.2rem",
  borderRadius: "6px",
  border: "none",
  backgroundColor: "#007bff",
  color: "white",
  fontSize: "1rem",
  cursor: "pointer",
  transition: "background-color 0.2s",
};

export default App;