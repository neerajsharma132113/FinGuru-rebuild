import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function formatMoney(value) {
  return value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function formatRate(value) {
  return value === null ? "—" : value + "%";
}

function DigitalTwin({ latest }) {
  const [income, setIncome] = useState("80000");
  const [expenses, setExpenses] = useState("40000");
  const [change, setChange] = useState(-20);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function useLatestMonth() {
    if (latest) {
      setIncome(String(latest.income));
      setExpenses(String(latest.expenses));
    }
  }

  async function handleSimulate(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    const params = new URLSearchParams({
      monthly_income: income,
      monthly_expenses: expenses,
      income_change_percent: change,
    });

    try {
      const response = await fetch(API_URL + "/simulate/income-change?" + params.toString());
      if (!response.ok) {
        setError("Please check the values (income must be above 0, expenses cannot be negative)");
        return;
      }
      setResult(await response.json());
    } catch (err) {
      setError("API not reachable");
    }
  }

  return (
    <div className="card">
      <h2>Digital Twin: what if my income changes?</h2>
      <form className="stack" onSubmit={handleSimulate}>
        <div className="form-row">
          <input
            type="number"
            step="0.01"
            placeholder="Monthly income (₹)"
            value={income}
            onChange={(e) => setIncome(e.target.value)}
            required
          />
          <input
            type="number"
            step="0.01"
            placeholder="Monthly expenses (₹)"
            value={expenses}
            onChange={(e) => setExpenses(e.target.value)}
            required
          />
          <button type="button" className="ghost" onClick={useLatestMonth} disabled={!latest}>
            Use latest month
          </button>
        </div>

        <label className="slider-label">
          Income change: <strong>{change > 0 ? "+" : ""}{change}%</strong>
        </label>
        <input
          type="range"
          min="-100"
          max="50"
          step="5"
          value={change}
          onChange={(e) => setChange(Number(e.target.value))}
        />

        <button type="submit">Simulate</button>
      </form>
      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <div className="compare">
            <div className="card stat">
              <p className="stat-label">Before</p>
              <p className="stat-line">Income ₹{formatMoney(result.before.income)}</p>
              <p className="stat-value green">₹{formatMoney(result.before.savings)}</p>
              <p className="stat-line">Savings rate {formatRate(result.before.savings_rate_percent)}</p>
            </div>
            <div className="card stat">
              <p className="stat-label">After</p>
              <p className="stat-line">Income ₹{formatMoney(result.after.income)}</p>
              <p className={"stat-value " + (result.after.savings >= 0 ? "green" : "red")}>
                ₹{formatMoney(result.after.savings)}
              </p>
              <p className="stat-line">Savings rate {formatRate(result.after.savings_rate_percent)}</p>
            </div>
          </div>
          <p className="note">
            Assumption: your expenses stay the same. This is a simple what-if estimate, not financial advice.
          </p>
        </>
      )}
    </div>
  );
}

export default DigitalTwin;