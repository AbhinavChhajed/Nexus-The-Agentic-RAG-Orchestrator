import "../App.css";
import { useState,} from "react";

interface Message {
  role: "user" | "Nexus";
  content: string;
}

function ChatArea() {
  const [files, setFiles] = useState<File[]>([]);
  const [prompt, setPrompt] = useState<string>("");

  const [messages, setmessages] = useState<Message[]>([
    { role: "Nexus", content: "Hello. I am ready to help." },
  ]);

  const upload = async () => {
    if (files.length === 0) return;

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file); // MUST match FastAPI param
    });

    const res = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    console.log(data);
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    setFiles(Array.from(e.target.files));
  };

  const handlePromptChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPrompt(e.target.value);
  };

  const handleSend = async () => {
    if (prompt.trim() === "") return;

    const current_prompt = prompt;

    setmessages((perv) => [...perv, { role: "user", content: current_prompt }]);
    setPrompt("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: current_prompt }),
      });

      const data = await res.json();

      setmessages((prev) => [
        ...prev,
        { role: "Nexus", content: data.response },
      ]);
    } catch (error) {
      console.error("Chat Error:", error);
      setmessages((prev) => [
        ...prev,
        { role: "Nexus", content: "Error: Could not reach backend." },
      ]);
    }
  };

  return (
    <main className="chat-area">
      <div className="messages-container">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message-wrapper ${
              msg.role === "user" ? "User" : "Nexus"
            }`}
          >
            <strong className="message-sender">{msg.role}:</strong>
            <p className="message-text">{msg.content}</p>
          </div>
        ))}
      </div>

      <div className="input-section">
        <input
          className="chat-input"
          type="text"
          placeholder="Send a message..."
          value={prompt}
          onChange={handlePromptChange}
        />
        <button className="send-btn" onClick={handleSend}>
          Send
        </button>

        <div>
          <input type="file" multiple onChange={handleFile} />
          <button onClick={upload}>Upload Files</button>
        </div>
      </div>
    </main>
  );
}

export default ChatArea;
