import { useState, useRef, useEffect } from "react";
import { askQuestion } from "../services/api";

function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async () => {
    if (!question.trim()) return;

    const userLocal = JSON.parse(localStorage.getItem("user"));
    const userEmail = userLocal?.email || "thunguyen465933@gmail.com"; 

    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await askQuestion(question, userEmail);
      
      const answer = res?.data?.answer || res?.answer || "AI chưa tìm thấy thông tin này.";
      setMessages((prev) => [...prev, { role: "ai", text: answer }]);
    } catch (error) {
      console.error("Lỗi chat:", error);
      setMessages((prev) => [...prev, { role: "ai", text: "Lỗi kết nối server!" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <div className="card">
        <h2 style={{ textAlign: "center", color: "var(--serenity)" }}>AI Assistant</h2>

        <div className="chat-container">
          {messages.map((m, i) => (
            <div key={i} className={m.role === "user" ? "msg-user" : "msg-ai"}>
              {m.text}
            </div>
          ))}

          {loading && (
            <div className="msg-ai typing">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          )}
          <div ref={bottomRef}></div>
        </div>

        <div style={{ display: "flex", marginTop: "15px" }}>
          <input
            className="input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Bạn muốn hỏi gì..."
          />
          <button className="btn" onClick={send}>Gửi</button>
        </div>
      </div>
    </div>
  );
}

export default Chat;