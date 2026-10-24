import { useState, useEffect } from "react";
import EmiCalculator from "./EmiCalculator";
import DigitalTwin from "./DigitalTwin";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

const API_URL = "http://127.0.0.1:8000";

function Dashboard({ token, userEmail, onLogout }) {
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState([]);
  const [date, setDate] = useState("");
  const [category, setCategory] = useState("");
  const [kind, setKind] = useState("expense");
  const [amount, setAmount] = useState("");
  const [error, setError] = useState("");

  async function loadTransactions() {
    const response = await fetch(API_URL + "/transactions", {
      headers: { Authorization: "Bearer " + token },
    });

    if (response.status === 401) {
      onLogout();
      return;
    }
    if (!response.ok) {
      setError("Could not load transactions");
      return;
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
    if (response.ok) {
      setSummary(await response.json());
    }
  }

  useEffect(() => {
    loadTransactions();
    loadSummary();
  }, []);

  async function handleAdd(event) {
    event.preventDefault();
    setError("");

    const response = await fetch(API_URL + "/transactions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({
        date: date,
        category: category,
        kind: kind,
        amount: Number(amount),
      }),
    });

    if (response.status === 401) {
      onLogout();
      return;
    }
    if (!response.ok) {
      setError("Please check the fields (amount must be above 0)");
      return;
    }

    setCategory("");
    setAmount("");
    loadTransactions();
    loadSummary();
  }

  function formatMoney(value) {
    return value.toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  const latest = summary.length > 0 ? summary[summary.length - 1] : null;

  return (
    <div className="page">
      <div className="topbar">
        <h1 className="brand">FinGuru</h1>
        <div className="topbar-right">
          <span className="user-chip">{userEmail}</span>
          <button className="ghost" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>

      {latest && (
        <div className="stats">
          <div className="card stat">
            <p className="stat-label">Income · {latest.month}</p>
            <p className="stat-value green">₹{formatMoney(latest.income)}</p>
          </div>
          <div className="card stat">
            <p className="stat-label">Expenses · {latest.month}</p>
            <p className="stat-value red">₹{formatMoney(latest.expenses)}</p>
          </div>
          <div className="card stat">
            <p className="stat-label">Savings</p>
            <p className={"stat-value " + (latest.savings >= 0 ? "green" : "red")}>
              ₹{formatMoney(latest.savings)}
            </p>
          </div>
          <div className="card stat">
            <p className="stat-label">Savings rate</p>
            <p className="stat-value">
              {latest.savings_rate_percent === null ? "—" : latest.savings_rate_percent + "%"}
            </p>
          </div>
        </div>
      )}

      {summary.length > 0 && (
        <div className="card">
          <h2>Income vs expenses by month</h2>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summary}>
                <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
                <XAxis dataKey="month" stroke="#8b90a7" />
                <YAxis stroke="#8b90a7" />
                <Tooltip
                  formatter={(value) => "₹" + formatMoney(value)}
                  contentStyle={{
                    background: "#161a26",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 10,
                  }}
                  cursor={{ fill: "rgba(255,255,255,0.05)" }}
                />
                <Legend />
                <Bar dataKey="income" name="Income" fill="#34d399" radius={[6, 6, 0, 0]} />
                <Bar dataKey="expenses" name="Expenses" fill="#fb7185" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
      <EmiCalculator />
      <DigitalTwin latest={latest} />
      <div className="card">
        <h2>Add transaction</h2>
        <form className="form-row" onSubmit={handleAdd}>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
          <input
            type="text"
            placeholder="Category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            required
          />
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
          <input
            type="number"
            step="0.01"
            placeholder="Amount (₹)"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
          />
          <button type="submit">Add</button>
        </form>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="card">
        <h2>Your transactions</h2>
        {transactions.length === 0 ? (
          <p className="empty">No transactions yet. Add your first one above.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Category</th>
                <th>Type</th>
                <th style={{ textAlign: "right" }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t) => (
                <tr key={t.id}>
                  <td>{t.date}</td>
                  <td>{t.category}</td>
                  <td>
                    <span className={"pill " + t.kind}>{t.kind}</span>
                  </td>
                  <td className={"amount " + t.kind}>
                    {t.kind === "income" ? "+" : "−"}₹{formatMoney(t.amount)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Dashboard;