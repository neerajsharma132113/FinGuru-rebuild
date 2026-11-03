import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { API_URL } from "../config";

function SignIn({ onLoggedIn }) {
  const location = useLocation();
  const startMode = location.state && location.state.mode === "register" ? "register" : "signin";

  const [mode, setMode] = useState(startMode);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function switchMode(newMode) {
    setMode(newMode);
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setBusy(true);

    try {
      if (mode === "register") {
        const created = await fetch(API_URL + "/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email, password: password }),
        });
        if (created.status === 409) {
          setError("That email is already registered. Try signing in.");
          return;
        }
        if (created.status === 403) {
          setError("Signups are closed for this demo.");
          return;
        }
        if (!created.ok) {
          setError("Enter a valid email and a password of at least 8 characters.");
          return;
        }
      }

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

      onLoggedIn(data.access_token, me.email);
    } catch (err) {
      setError("The server could not be reached.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-wrap">
      <div className="card login-card">
        <Link to="/" className="brand">FinGuru</Link>
        <p className="subtitle">
          {mode === "signin" ? "Sign in to your account" : "Create your account"}
        </p>

        <div className="tabs">
          <button
            type="button"
            className={"tab " + (mode === "signin" ? "active" : "")}
            onClick={() => switchMode("signin")}
          >
            Sign in
          </button>
          <button
            type="button"
            className={"tab " + (mode === "register" ? "active" : "")}
            onClick={() => switchMode("register")}
          >
            Create account
          </button>
        </div>

        <form className="stack" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder={mode === "register" ? "Password (at least 8 characters)" : "Password"}
            autoComplete={mode === "register" ? "new-password" : "current-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" disabled={busy}>
            {busy ? "Please wait..." : mode === "signin" ? "Sign in" : "Create account"}
          </button>
        </form>
        {busy && <p className="note">The free demo server can take up to a minute to wake up. Please wait.</p>}
        {error && <p className="error">{error}</p>}

        <Link to="/" className="back-link">← Back to home</Link>
      </div>
    </div>
  );
}

export default SignIn;