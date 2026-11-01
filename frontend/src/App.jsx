import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./Dashboard";
import Landing from "./pages/Landing";
import SignIn from "./pages/SignIn";
import Overview from "./pages/Overview";
import Transactions from "./pages/Transactions";
import Loans from "./pages/Loans";
import Simulate from "./pages/Simulate";
import Fraud from "./pages/Fraud";
import Ask from "./pages/Ask";

function App() {
  const [token, setToken] = useState(null);
  const [userEmail, setUserEmail] = useState("");

  function handleLoggedIn(newToken, email) {
    setToken(newToken);
    setUserEmail(email);
  }

  function handleLogout() {
    setToken(null);
    setUserEmail("");
  }

  return (
    <BrowserRouter>
      {token ? (
        <Routes>
          <Route
            element={<Dashboard token={token} userEmail={userEmail} onLogout={handleLogout} />}
          >
            <Route path="/overview" element={<Overview />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/loans" element={<Loans />} />
            <Route path="/simulate" element={<Simulate />} />
            <Route path="/fraud" element={<Fraud />} />
            <Route path="/ask" element={<Ask />} />
          </Route>
          <Route path="*" element={<Navigate to="/overview" replace />} />
        </Routes>
      ) : (
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/signin" element={<SignIn onLoggedIn={handleLoggedIn} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      )}
    </BrowserRouter>
  );
}

export default App;