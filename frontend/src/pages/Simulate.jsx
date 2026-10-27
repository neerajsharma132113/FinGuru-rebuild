import { useOutletContext } from "react-router-dom";
import DigitalTwin from "../DigitalTwin";
import NextBestAction from "../NextBestAction";

function Simulate() {
  const { latest } = useOutletContext();

  return (
    <div>
      <h2 className="page-title">Simulate</h2>
      <DigitalTwin latest={latest} />
      <NextBestAction latest={latest} />
    </div>
  );
}

export default Simulate;