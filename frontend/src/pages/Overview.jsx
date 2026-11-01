import { Link, useOutletContext } from "react-router-dom";
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

function newestFirst(a, b) {
  if (a.date > b.date) {
    return -1;
  }
  if (a.date < b.date) {
    return 1;
  }
  return b.id - a.id;
}

function shortMoney(value) {
  if (value >= 100000) {
    return (value / 100000).toFixed(1) + "L";
  }
  if (value >= 1000) {
    return Math.round(value / 1000) + "k";
  }
  return String(value);
}

function Overview() {
  const { summary, latest, transactions } = useOutletContext();

  if (!latest) {
    return (
      <div>
        <div className="page-head">
          <h2 className="page-title">Overview</h2>
        </div>
        <div className="card">
          <p className="empty">
            Nothing to show yet. Add a few transactions and your month at a glance will appear here.
          </p>
          <p style={{ textAlign: "center", margin: 0 }}>
            <Link className="btn" to="/transactions">Add a transaction</Link>
          </p>
        </div>
      </div>
    );
  }

  const recent = [...transactions].sort(newestFirst).slice(0, 5);
  const chartData = summary.slice(-12);

  return (
    <div>
      <div className="page-head">
        <h2 className="page-title">Overview</h2>
        <span className="page-meta">Latest month: {latest.month}</span>
      </div>

      <div className="stats">
        <div className="card stat">
          <p className="stat-label">Income</p>
          <p className="stat-value green">₹{formatMoney(latest.income)}</p>
        </div>
        <div className="card stat">
          <p className="stat-label">Expenses</p>
          <p className="stat-value">₹{formatMoney(latest.expenses)}</p>
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

      <div className="split">
        <div className="card">
          <div className="panel-head">
            <h2>Income and expenses by month</h2>
          </div>
          <div style={{ width: "100%", height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 4, right: 4, left: -12, bottom: 0 }}>
                <CartesianGrid stroke="#252a33" vertical={false} />
                <XAxis
                  dataKey="month"
                  stroke="#6a7180"
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  stroke="#6a7180"
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={shortMoney}
                />
                <Tooltip
                  formatter={(value) => "₹" + formatMoney(value)}
                  contentStyle={{
                    background: "#14171c",
                    border: "1px solid #323946",
                    borderRadius: 6,
                    fontSize: 12,
                  }}
                  cursor={{ fill: "rgba(255,255,255,0.04)" }}
                />
                <Legend iconSize={8} wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="income" name="Income" fill="#4cb782" barSize={12} />
                <Bar dataKey="expenses" name="Expenses" fill="#7d8596" barSize={12} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="panel-head">
            <h2>Recent transactions</h2>
            <Link className="link-quiet" to="/transactions">View all</Link>
          </div>
          <ul className="recent">
            {recent.map((t) => (
              <li key={t.id}>
                <span>
                  <span className="recent-main">{t.category}</span>
                  <span className="recent-date">{t.date}</span>
                </span>
                <span className={"amount " + t.kind}>
                  {t.kind === "income" ? "+" : "−"}₹{formatMoney(t.amount)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Overview;