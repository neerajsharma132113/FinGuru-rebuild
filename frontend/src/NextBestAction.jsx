import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function formatMoney(value) {
  return value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

const ACTION_CLASS = {
  HELP: "help",
  WARN: "warn",
  SAVE: "save",
  "NO ACTION": "none",
};

function NextBestAction({ latest }) {
  const [income, setIncome] = useState("80000");
  const [expenses, setExpenses] = useState("40000");
  const [emi, setEmi] = useState("10000");
  const [fund, setFund] = useState("60000");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function useLatestMonth() {
    if (latest) {
      setIncome(String(latest.income));
      setExpenses(String(latest.expenses));
    }
  }

  async function handleCheck(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    const params = new URLSearchParams({
      monthly_income: income,
      monthly_expenses: expenses,
      monthly_emi: emi,
      emergency_fund: fund,
    });

    try {
      const response = await fetch(API_URL + "/next-best-action?" + params.toString());
      if (!response.ok) {
        setError("Please check the values (income must be above 0, others cannot be negative)");
        return;
      }
      setResult(await response.json());
    } catch (err) {
      setError("API not reachable");
    }
  }

  return (
    <div className="card">
      <h2>Next best action</h2>
      <form className="stack" onSubmit={handleCheck}>
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
            placeholder="Total monthly spending (₹)"
            value={expenses}
            onChange={(e) => setExpenses(e.target.value)}
            required
          />
          <button type="button" className="ghost" onClick={useLatestMonth} disabled={!latest}>
            Use latest month
          </button>
        </div>
        <div className="form-row">
          <input
            type="number"
            step="0.01"
            placeholder="Monthly EMIs (₹)"
            value={emi}
            onChange={(e) => setEmi(e.target.value)}
            required
          />
          <input
            type="number"
            step="0.01"
            placeholder="Emergency fund (₹)"
            value={fund}
            onChange={(e) => setFund(e.target.value)}
            required
          />
        </div>
        <button type="submit">Get recommendation</button>
      </form>
      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <div className={"action-box " + ACTION_CLASS[result.action]}>
            <p className="action-name">{result.action}</p>
            <p className="action-reason">{result.reason}</p>
          </div>
          <div className="compare">
            <div className="card stat">
              <p className="stat-label">Monthly savings</p>
              <p className="stat-value">₹{formatMoney(result.details.monthly_savings)}</p>
            </div>
            <div className="card stat">
              <p className="stat-label">EMI share of income</p>
              <p className="stat-value">{result.details.emi_to_income_percent}%</p>
            </div>
            <div className="card stat">
              <p className="stat-label">Emergency fund target</p>
              <p className="stat-value">₹{formatMoney(result.details.emergency_fund_target)}</p>
            </div>
          </div>
          <p className="note">
            Rules used: spending above income → HELP; EMIs above 40% of income → WARN; emergency fund
            under 3 months of spending → SAVE. These thresholds are assumptions, and this is not
            financial advice.
          </p>
        </>
      )}
    </div>
  );
}

export default NextBestAction;