import { useState } from "react";
import { addUser, getMatches, addSession, getProgress } from "./api";

function App() {
  const [userId, setUserId] = useState(null);
  const [matches, setMatches] = useState([]);
  const [progress, setProgress] = useState([]);

  const handleAddUser = async () => {
    const newUser = {
      name: "Alice",
      skills_known: ["Python"],
      skills_want: ["Java"],
      location: "Delhi",
    };
    const res = await addUser(newUser);
    setUserId(res.user_id);
    alert(`User added with ID: ${res.user_id}`);
  };

  const handleGetMatches = async () => {
    if (!userId) return alert("Add a user first!");
    const data = await getMatches(userId);
    setMatches(data);
  };

  const handleAddSession = async () => {
    if (!userId) return alert("Add a user first!");
    const sessionData = {
      user_id: userId,
      teacher_id: 2,
      skill: "Python",
      session_notes: "Practiced OOP basics",
    };
    await addSession(sessionData);
    alert("Session added!");
  };

  const handleGetProgress = async () => {
    if (!userId) return alert("Add a user first!");
    const data = await getProgress(userId);
    setProgress(data);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>SkillSwap Frontend</h1>

      <button onClick={handleAddUser}>Add User</button>
      <button onClick={handleGetMatches}>Get Matches</button>
      <button onClick={handleAddSession}>Add Session</button>
      <button onClick={handleGetProgress}>Get Progress</button>

      <h2>Matches</h2>
      <ul>
        {matches.map((m) => (
          <li key={m.id}>
            {m.name} - knows {m.skills_known}, wants {m.skills_want}
          </li>
        ))}
      </ul>

      <h2>Progress</h2>
      <ul>
        {progress.map((p) => (
          <li key={p.session_id}>
            {p.skill} → {p.session_notes} ({p.timestamp})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
