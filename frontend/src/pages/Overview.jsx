import { useOutletContext } from "react-router-dom";
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
import { formatMoney } from "../format";

function Overview() {
  const { summary, latest } = useOutletContext();

  return (
    <div>
      <h2 className="page-title">Overview</h2>

      {!latest && <p className="empty">No data yet. Add transactions on the Transactions screen.</p>}

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
    </div>
  );
}

export default Overview;