import { useState, useEffect } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { API_URL } from "./config";

function Dashboard({ token, userEmail, onLogout }) {
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState([]);

  async function loadTransactions() {
    const response = await fetch(API_URL + "/transactions", {
      headers: { Authorization: "Bearer " + token },
    });
    if (response.status === 401) {
      onLogout();
      return;
    }
    if (response.ok) {
      setTransactions(await response.json());
    }
  }

  async function loadSummary() {
    const response = await fetch(API_URL + "/summary", {
      headers: { Authorization: "Bearer " + token },
    });
    if (response.status === 401) {
      onLogout();
      return;
    }
    if (response.ok) {
      setSummary(await response.json());
    }
  }

  function reload() {
    loadTransactions();
    loadSummary();
  }

  useEffect(() => {
    reload();
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
          <NavLink to="/fraud" className="nav-link">Fraud</NavLink>
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
        <Outlet context={{ token, onLogout, transactions, summary, latest, reload }} />
      </main>
    </div>
  );
}

export default Dashboard;