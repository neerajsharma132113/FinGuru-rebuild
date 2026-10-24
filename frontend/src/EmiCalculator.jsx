import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function formatMoney(value) {
  return value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function EmiCalculator() {
  const [principal, setPrincipal] = useState("500000");
  const [rate, setRate] = useState("10");
  const [months, setMonths] = useState("60");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleCalculate(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    const params = new URLSearchParams({
      principal: principal,
      annual_rate_percent: rate,
      tenure_months: months,
    });

    try {
      const response = await fetch(API_URL + "/emi?" + params.toString());

      if (!response.ok) {
        setError("Please check the values (amount and months must be above 0, rate cannot be negative)");
        return;
      }
      setResult(await response.json());
    } catch (err) {
      setError("API not reachable");
    }
  }

  return (
    <div className="card">
      <h2>Loan EMI calculator</h2>
      <form className="form-row" onSubmit={handleCalculate}>
        <input
          type="number"
          step="0.01"
          placeholder="Loan amount (₹)"
          value={principal}
          onChange={(e) => setPrincipal(e.target.value)}
          required
        />
        <input
          type="number"
          step="0.01"
          placeholder="Yearly interest (%)"
          value={rate}
          onChange={(e) => setRate(e.target.value)}
          required
        />
        <input
          type="number"
          placeholder="Tenure (months)"
          value={months}
          onChange={(e) => setMonths(e.target.value)}
          required
        />
        <button type="submit">Calculate</button>
      </form>
      {error && <p className="error">{error}</p>}

      {result && (
        <div className="stats" style={{ marginTop: 16 }}>
          <div className="card stat">
            <p className="stat-label">Monthly EMI</p>
            <p className="stat-value">₹{formatMoney(result.emi)}</p>
          </div>
          <div className="card stat">
            <p className="stat-label">Total interest</p>
            <p className="stat-value red">₹{formatMoney(result.total_interest)}</p>
          </div>
          <div className="card stat">
            <p className="stat-label">Total payment</p>
            <p className="stat-value">₹{formatMoney(result.total_payment)}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default EmiCalculator;