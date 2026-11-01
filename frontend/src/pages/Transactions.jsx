import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import { formatMoney } from "../format";

import { API_URL } from "../config"

function Transactions() {
  const { token, onLogout, transactions, reload } = useOutletContext();
  const [date, setDate] = useState("");
  const [category, setCategory] = useState("");
  const [kind, setKind] = useState("expense");
  const [amount, setAmount] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  function clearForm() {
    setDate("");
    setCategory("");
    setKind("expense");
    setAmount("");
    setEditingId(null);
  }

  function startEdit(t) {
    setDate(t.date);
    setCategory(t.category);
    setKind(t.kind);
    setAmount(String(t.amount));
    setEditingId(t.id);
    setError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    const url = editingId === null ? "/transactions" : "/transactions/" + editingId;
    const method = editingId === null ? "POST" : "PUT";

    const response = await fetch(API_URL + url, {
      method: method,
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

    clearForm();
    reload();
  }

  async function handleDelete(id, label) {
    const sure = window.confirm("Delete this transaction (" + label + ")? This cannot be undone.");
    if (!sure) {
      return;
    }
    setError("");

    const response = await fetch(API_URL + "/transactions/" + id, {
      method: "DELETE",
      headers: { Authorization: "Bearer " + token },
    });

    if (response.status === 401) {
      onLogout();
      return;
    }
    if (!response.ok) {
      setError("Could not delete that transaction");
      return;
    }
    if (id === editingId) {
      clearForm();
    }
    reload();
  }

  return (
    <div>
      <h2 className="page-title">Transactions</h2>

      <div className="card">
        <h2>{editingId === null ? "Add transaction" : "Edit transaction"}</h2>
        <form className="form-row" onSubmit={handleSubmit}>
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
          <button type="submit">{editingId === null ? "Add" : "Save changes"}</button>
          {editingId !== null && (
            <button type="button" className="ghost" onClick={clearForm}>
              Cancel
            </button>
          )}
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
                <th></th>
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
                  <td style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                    <button className="ghost small" onClick={() => startEdit(t)}>
                      Edit
                    </button>{" "}
                    <button
                      className="danger"
                      onClick={() => handleDelete(t.id, t.category + " ₹" + formatMoney(t.amount))}
                    >
                      Delete
                    </button>
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

export default Transactions;