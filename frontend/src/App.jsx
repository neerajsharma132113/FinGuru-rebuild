import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);
  const [userEmail, setUserEmail] = useState("");
  const [error, setError] = useState("");

  async function handleLogin(event) {
    event.preventDefault(); // stop the browser from reloading the page
    setError("");

    try {
      const response = await fetch(API_URL + "/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password }),
      });

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
    return (
      <div>
        <h1>FinGuru</h1>
        <p>Logged in as {userEmail}</p>
        <button onClick={handleLogout}>Logout</button>
      </div>
    );
  }

  return (
    <div>
      <h1>FinGuru</h1>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <br />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <br />
        <button type="submit">Login</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default App;