import { useOutletContext } from "react-router-dom";
import EmiCalculator from "../EmiCalculator";
import LoanScenario from "../LoanScenario";

function Loans() {
  const { latest } = useOutletContext();

  return (
    <div>
      <h2 className="page-title">Loans</h2>
      <EmiCalculator />
      <LoanScenario latest={latest} />
    </div>
  );
}

export default Loans;