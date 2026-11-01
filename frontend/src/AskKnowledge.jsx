import { useState, useRef, useEffect } from "react";

import { API_URL } from "./config";

const GREETING = {
  role: "bot",
  text: "Hi! Ask me about EMIs, emergency funds or savings rate. I answer only from FinGuru's short knowledge notes, and I will say so when I can't find something.",
  sources: [],
};

function AskKnowledge({ token, onLogout }) {
  const [messages, setMessages] = useState([GREETING]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  // Scroll to the newest message whenever the list changes
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [messages]);

  async function handleSend(event) {
    event.preventDefault();
    const text = question.trim();
    if (text.length < 3 || loading) {
      return;
    }

    setMessages((old) => [...old, { role: "user", text: text, sources: [] }]);
    setQuestion("");
    setLoading(true);

    let botMessage;
    try {
      const params = new URLSearchParams({ question: text });
      const response = await fetch(API_URL + "/ask?" + params.toString(), {
        headers: { Authorization: "Bearer " + token },
      });

      if (response.status === 401) {
        onLogout();
        return;
      }

      if (!response.ok) {
        botMessage = { role: "bot", text: "Please type a question of 3 to 300 characters.", sources: [] };
      } else {
        const data = await response.json();
        botMessage = { role: "bot", text: data.message, sources: data.sources };
      }
    } catch (err) {
      botMessage = { role: "bot", text: "I could not reach the API.", sources: [] };
    }

    setMessages((old) => [...old, botMessage]);
    setLoading(false);
  }

  return (
    <div className="card chat">
      <div className="chat-header">
        <h2>Ask FinGuru notes</h2>
        <button className="ghost" onClick={() => setMessages([GREETING])}>
          Clear chat
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((m, index) => (
          <div key={index} className={"bubble " + m.role}>
            <p className="bubble-text">{m.text}</p>
            {m.sources.map((s) => (
              <div className="source-box" key={s.id}>
                <p className="stat-label">{s.source}</p>
                <p className="source-text">{s.text}</p>
              </div>
            ))}
          </div>
        ))}
        {loading && (
          <div className="bubble bot">
            <p className="bubble-text">Searching the notes...</p>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form className="chat-input" onSubmit={handleSend}>
        <input
          type="text"
          maxLength={300}
          placeholder="Type your question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          Send
        </button>
      </form>

      <p className="note">
        Each question is answered on its own, so I don't remember earlier messages. These notes are
        general education, not financial advice, and they do not cover regulations, tax or
        investments.
      </p>
    </div>
  );
}

export default AskKnowledge;