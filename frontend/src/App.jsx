import { useMemo, useState } from "react";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function createSessionId() {
  return `web-${Math.random().toString(36).slice(2, 10)}`;
}

export default function App() {
  const [sessionId] = useState(createSessionId);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const canSubmit = useMemo(() => question.trim().length > 1 && !loading, [question, loading]);

  async function askQuestion(event) {
    event.preventDefault();
    if (!canSubmit) return;

    const currentQuestion = question.trim();
    setQuestion("");
    setError("");

    setMessages((prev) => [...prev, { role: "user", text: currentQuestion }]);
    setLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          question: currentQuestion,
        }),
      });

      const payload = await response.json();

      if (!response.ok) {
        const message = payload?.detail || "Request failed.";
        setError(message);
        setMessages((prev) => [...prev, { role: "assistant", text: `Error: ${message}` }]);
        return;
      }

      setMessages((prev) => [...prev, { role: "assistant", text: payload.answer }]);
    } catch {
      const message = "Could not reach backend API.";
      setError(message);
      setMessages((prev) => [...prev, { role: "assistant", text: `Error: ${message}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">Intelligent Bank FAQ Agent</h1>
        <p className="subtext">Ask banking or NBFC-related questions and get tool-augmented answers.</p>

        <form onSubmit={askQuestion}>
          <div className="row">
            <input
              className="input"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Example: How is EMI calculated for a 5 lakh loan?"
            />
            <button className="button" type="submit" disabled={!canSubmit}>
              {loading ? "Asking..." : "Ask"}
            </button>
          </div>
        </form>

        <div className="messages">
          {messages.length === 0 ? (
            <div className="msg">
              <div className="meta">Assistant</div>
              Ask your first question.
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`msg ${message.role === "user" ? "user" : ""}`}>
                <div className="meta">{message.role === "user" ? "You" : "Assistant"}</div>
                {message.text}
              </div>
            ))
          )}
        </div>

        {error ? <p className="error">{error}</p> : null}
      </div>
    </div>
  );
}
