import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import { formatMoney } from "../format";

const API_URL = "http://127.0.0.1:8000";

function Transactions() {
  const { token, onLogout, transactions, reload } = useOutletContext();
  const [date, setDate] = useState("");
  const [category, setCategory] = useState("");
  const [kind, setKind] = useState("expense");
  const [amount, setAmount] = useState("");
  const [error, setError] = useState("");

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
    reload();
  }

  return (
    <div>
      <h2 className="page-title">Transactions</h2>

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
                  <td style={{ textAlign: "right" }}>
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