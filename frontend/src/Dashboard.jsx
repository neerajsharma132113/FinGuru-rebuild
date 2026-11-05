import { useState, useEffect } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { API_URL } from "./config";

function Dashboard({ token, userEmail, onLogout }) {
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [slow, setSlow] = useState(false);

  async function loadTransactions() {
    const response = await fetch(API_URL + "/transactions", {
      headers: { Authorization: "Bearer " + token },
    });
    if (response.status === 401) {
      onLogout();
      return;
    }
    if (!response.ok) {
      throw new Error("transactions failed");
    }
    setTransactions(await response.json());
  }

  async function loadSummary() {
    const response = await fetch(API_URL + "/summary", {
      headers: { Authorization: "Bearer " + token },
    });
    if (response.status === 401) {
      onLogout();
      return;
    }
    if (!response.ok) {
      throw new Error("summary failed");
    }
    setSummary(await response.json());
  }

  async function reload() {
    setLoadError("");
    try {
      await Promise.all([loadTransactions(), loadSummary()]);
    } catch (err) {
      setLoadError("Could not load your data. The free demo server may still be waking up.");
    }
    setLoaded(true);
  }

  useEffect(() => {
    reload();
  }, []);

  // After 4 seconds without data, show the "waking up" hint
  useEffect(() => {
    const timer = setTimeout(() => setSlow(true), 4000);
    return () => clearTimeout(timer);
  }, []);

  const latest = summary.length > 0 ? summary[summary.length - 1] : null;

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1 className="brand">FinGuru</h1>
        <nav className="nav">
          <NavLink to="/overview" className="nav-link">Overview</NavLink>
          <NavLink to="/transactions" className="nav-link">Transactions</NavLink>
          <NavLink to="/loans" className="nav-link">Loans</NavLink>
          <NavLink to="/simulate" className="nav-link">Simulate</NavLink>
          <NavLink to="/fraud" className="nav-link">Risk Analyzer</NavLink>
          <NavLink to="/ask" className="nav-link">Ask</NavLink>
        </nav>
        <div className="sidebar-bottom">
          <span className="user-chip">{userEmail}</span>
          <button className="ghost" onClick={onLogout}>
            Logout
          </button>
        </div>
      </aside>

      <main className="content">
        <Outlet
          context={{
            token,
            onLogout,
            transactions,
            summary,
            latest,
            loaded,
            loadError,
            slow,
            reload,
          }}
        />
      </main>
    </div>
  );
}

export default Dashboard;