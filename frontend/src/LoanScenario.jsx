import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function formatMoney(value) {
  return value.toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

const VERDICT_TEXT = {
  ok: "Looks manageable",
  stretched: "Stretched: EMI is above 40% of income",
  unaffordable: "Unaffordable: savings would go negative",
};

function LoanScenario({ latest }) {
  const [income, setIncome] = useState("80000");
  const [expenses, setExpenses] = useState("40000");
  const [loanAmount, setLoanAmount] = useState("500000");
  const [rate, setRate] = useState("10");
  const [months, setMonths] = useState("60");
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
      loan_amount: loanAmount,
      annual_rate_percent: rate,
      tenure_months: months,
    });

    try {
      const response = await fetch(API_URL + "/simulate/loan?" + params.toString());
      if (!response.ok) {
        setError("Please check the values (amounts and months must be above 0)");
        return;
      }
      setResult(await response.json());
    } catch (err) {
      setError("API not reachable");
    }
  }

  return (
    <div className="card">
      <h2>Digital Twin: what if I take a loan?</h2>
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
        <div className="form-row">
          <input
            type="number"
            step="0.01"
            placeholder="Loan amount (₹)"
            value={loanAmount}
            onChange={(e) => setLoanAmount(e.target.value)}
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
        </div>
        <button type="submit">Simulate loan</button>
      </form>
      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <div className={"verdict " + result.verdict}>{VERDICT_TEXT[result.verdict]}</div>
          <div className="compare">
            <div className="card stat">
              <p className="stat-label">New monthly EMI</p>
              <p className="stat-value">₹{formatMoney(result.emi)}</p>
              <p className="stat-line">{result.emi_to_income_percent}% of income</p>
              <p className="stat-line">Total interest ₹{formatMoney(result.total_interest)}</p>
            </div>
            <div className="card stat">
              <p className="stat-label">Monthly savings</p>
              <p className="stat-line">Before: ₹{formatMoney(result.savings_before)}</p>
              <p className={"stat-value " + (result.savings_after >= 0 ? "green" : "red")}>
                After: ₹{formatMoney(result.savings_after)}
              </p>
              <p className="stat-line">
                Savings rate {result.savings_rate_before_percent}% → {result.savings_rate_after_percent}%
              </p>
            </div>
          </div>
          <p className="note">
            Assumptions: income and other expenses stay the same, and 40% of income is used as the EMI
            limit. This is a simple what-if estimate, not financial advice.
          </p>
        </>
      )}
    </div>
  );
}

export default LoanScenario;