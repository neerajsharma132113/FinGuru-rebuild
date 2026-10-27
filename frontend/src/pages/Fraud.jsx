import { useOutletContext } from "react-router-dom";
import FraudCheck from "../FraudCheck";

function Fraud() {
  const { token, onLogout } = useOutletContext();

  return (
    <div>
      <h2 className="page-title">Fraud</h2>
      <FraudCheck token={token} onLogout={onLogout} />
    </div>
  );
}

export default Fraud;