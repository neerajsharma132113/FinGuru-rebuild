import { useOutletContext } from "react-router-dom";
import AskKnowledge from "../AskKnowledge";

function Ask() {
  const { token, onLogout } = useOutletContext();

  return (
    <div>
      <h2 className="page-title">Ask</h2>
      <AskKnowledge token={token} onLogout={onLogout} />
    </div>
  );
}

export default Ask;