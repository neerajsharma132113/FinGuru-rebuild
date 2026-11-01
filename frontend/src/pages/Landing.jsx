import { Link } from "react-router-dom";

const FEATURES = [
  {
    name: "Loans and EMI",
    text: "Work out the monthly payment, the full repayment schedule and how much loan you can afford.",
  },
  {
    name: "Digital Twin",
    text: "Test a decision on paper first: a drop in income, or a new loan, shown before and after.",
  },
  {
    name: "Next best action",
    text: "One clear suggestion from readable rules, with the reason and the numbers behind it.",
  },
  {
    name: "Fraud check",
    text: "Score a transaction and see the main factors. It flags for review and never blocks anything.",
  },
  {
    name: "Ask the notes",
    text: "Answers come only from reviewed notes, and it says so when it cannot find something.",
  },
];

function Landing() {
  return (
    <div className="land">
      <header className="land-header">
        <Link to="/" className="brand">FinGuru</Link>
        <Link to="/signin" className="btn ghost">Sign in</Link>
      </header>

      <main className="land-main">
        <section className="hero">
          <div>
            <p className="eyebrow">Personal financial copilot</p>
            <h1 className="hero-title">Know where you stand before you decide.</h1>
            <p className="hero-text">
              FinGuru turns your income, spending and loans into clear numbers, tests decisions on
              paper first, and explains every suggestion it makes.
            </p>
            <div className="hero-actions">
              <Link to="/signin" state={{ mode: "register" }} className="btn">Get started</Link>
              <Link to="/signin" className="btn ghost">Sign in</Link>
            </div>
          </div>

          <div className="sample">
            <p className="sample-title">Example calculation</p>
            <p className="sample-sub">₹5,00,000 loan · 10% a year · 60 months</p>
            <div className="sample-row">
              <span>Monthly EMI</span>
              <strong>₹10,623.52</strong>
            </div>
            <div className="sample-row">
              <span>Total interest</span>
              <strong>₹1,37,411.34</strong>
            </div>
            <div className="sample-row">
              <span>Total payment</span>
              <strong>₹6,37,411.34</strong>
            </div>
          </div>
        </section>

        <section>
          <h2 className="section-label">What it does</h2>
          <div className="features">
            {FEATURES.map((feature) => (
              <div className="feature-row" key={feature.name}>
                <p className="feature-name">{feature.name}</p>
                <p className="feature-text">{feature.text}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="principles">
          <div>
            <h2 className="section-label">Tested arithmetic</h2>
            <p className="feature-text">
              Every figure comes from calculation code with automated tests. Nothing is estimated by
              a language model.
            </p>
          </div>
          <div>
            <h2 className="section-label">Explainable</h2>
            <p className="feature-text">
              Each suggestion shows its reason and the numbers it used, so you can check it yourself.
            </p>
          </div>
          <div>
            <h2 className="section-label">Private by design</h2>
            <p className="feature-text">
              Passwords are hashed, your records are visible only to you, and this demo is meant for
              made-up data only.
            </p>
          </div>
        </section>
      </main>

      <footer className="land-footer">
        An educational project using synthetic data. Not financial advice.
      </footer>
    </div>
  );
}

export default Landing;