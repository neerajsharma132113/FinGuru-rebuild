import { useState } from "react";
import Dashboard from "./dashboard";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);
  const [userEmail, setUserEmail] = useState("");
  const [error, setError] = useState("");

  async function handleLogin(event) {
    event.preventDefault();
    setError("");

    try {
      const response = await fetch(API_URL + "/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password }),
      });

      if (response.status === 429) {
        setError("Too many failed attempts. Try again in 15 minutes.");
        return;
      }

      if (!response.ok) {
        setError("Invalid email or password");
        return;
      }

      const data = await response.json();

      const meResponse = await fetch(API_URL + "/me", {
        headers: { Authorization: "Bearer " + data.access_token },
      });
      const me = await meResponse.json();

      setToken(data.access_token);
      setUserEmail(me.email);
      setPassword("");
    } catch (err) {
      setError("API not reachable");
    }
  }

  function handleLogout() {
    setToken(null);
    setUserEmail("");
  }

  if (token) {
    return <Dashboard token={token} userEmail={userEmail} onLogout={handleLogout} />;
  }

  return (
    <div className="login-wrap">
      <div className="card login-card">
        <h1 className="brand">FinGuru</h1>
        <p className="subtitle">Your personal financial copilot</p>
        <form className="stack" onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Login</button>
        </form>
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
}

export default App;