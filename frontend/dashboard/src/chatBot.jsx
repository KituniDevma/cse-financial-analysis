import React, { useState } from "react";
import "./chatBot.css"; // 👈 We'll style here

export default function ChatBot({ onClose }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    { sender: "bot", text: "👋 Hi! Ask me about revenues, net income..." },
  ]);

  const handleAsk = async () => {
    if (!question.trim()) return;

    // Add user message
    setMessages([...messages, { sender: "user", text: question }]);

    try {
      const res = await fetch("http://localhost:3001/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: data.answer || "⚠️ No answer received" },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "⚠️ Could not connect to backend" },
      ]);
    }

    setQuestion("");
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <span>ONLINE CHAT</span>
        <button className="close-btn" onClick={onClose}>✕</button>
      </div>

      <div className="chat-body">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.sender}`}>
            <div className="chat-icon">{msg.sender === "bot" ? "🎧" : "👤"}</div>
            <div className="chat-text">{msg.text}</div>
          </div>
        ))}
      </div>

      <div className="chat-footer">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question..."
        />
        <button onClick={handleAsk}>➤</button>
      </div>
    </div>
  );
}
