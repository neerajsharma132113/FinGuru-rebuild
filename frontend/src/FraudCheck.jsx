import { useState } from "react";

import { API_URL } from "./config";

function FraudCheck({ token, onLogout }) {
  const [amount, setAmount] = useState("450");
  const [hour, setHour] = useState("14");
  const [isForeign, setIsForeign] = useState("0");
  const [txns, setTxns] = useState("2");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleCheck(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    const params = new URLSearchParams({
      amount: amount,
      hour: hour,
      is_foreign: isForeign,
      txns_last_24h: txns,
    });

    try {
      const response = await fetch(API_URL + "/fraud-score?" + params.toString(), {
        headers: { Authorization: "Bearer " + token },
      });

      if (response.status === 401) {
        onLogout();
        return;
      }
      if (response.status === 503) {
        setError("Fraud model is not available. Run ml/train_final.py first.");
        return;
      }
      if (!response.ok) {
        setError("Please check the values (hour must be 0 to 23, amount above 0)");
        return;
      }
      setResult(await response.json());
    } catch (err) {
      setError("API not reachable");
    }
  }

  return (
    <div className="card">
      <h2>Transaction risk check</h2>
      <form className="stack" onSubmit={handleCheck}>
        <div className="form-row">
          <input
            type="number"
            step="0.01"
            placeholder="Amount (₹)"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
          />
          <input
            type="number"
            min="0"
            max="23"
            placeholder="Hour (0 to 23)"
            value={hour}
            onChange={(e) => setHour(e.target.value)}
            required
          />
          <select value={isForeign} onChange={(e) => setIsForeign(e.target.value)}>
            <option value="0">Domestic</option>
            <option value="1">Foreign</option>
          </select>
          <input
            type="number"
            min="0"
            placeholder="Transactions in last 24h"
            value={txns}
            onChange={(e) => setTxns(e.target.value)}
            required
          />
        </div>
        <button type="submit">Check transaction</button>
      </form>
      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <div className={"action-box " + (result.flagged ? "help" : "none")}>
            <p className="action-name">{result.flagged ? "FLAGGED FOR REVIEW" : "LOOKS NORMAL"}</p>
            <p className="action-reason">
              Fraud score {(result.fraud_score * 100).toFixed(1)}% (flag threshold{" "}
              {(result.threshold * 100).toFixed(0)}%)
            </p>
          </div>

          {result.reasons.length > 0 && (
            <div className="card stat" style={{ marginTop: 16 }}>
              <p className="stat-label">Main factors pushing the score up</p>
              <ul className="reasons">
                {result.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            </div>
          )}

          <p className="note">
            {result.note} A flag means "review this transaction". It does not block anything or prove
            fraud.
          </p>
        </>
      )}
    </div>
  );
}

export default FraudCheck;