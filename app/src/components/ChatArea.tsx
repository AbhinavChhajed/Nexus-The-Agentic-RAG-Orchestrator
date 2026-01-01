import "../App.css";
import { useState, useEffect } from "react";

interface TextContentObj {
    type?: string;
    text: string;
    [key: string]: unknown;
}

interface BackendMessage {
  role: string;
  content: string | TextContentObj; 
}

interface HistoryResponse {
  messages: BackendMessage[];
}

interface Message {
  role: "user" | "Nexus";
  content: string;
}

interface ChatAreaProps {
  threadId: string | null;
  onThreadCreated: (newId: string) => void;
}

function ChatArea({ threadId, onThreadCreated }: ChatAreaProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [prompt, setPrompt] = useState<string>("");
  
  const [messages, setMessages] = useState<Message[]>([
    { role: "Nexus", content: "Hello. I am ready to help." },
  ]);

  useEffect(() => {
    if (!threadId) return;

    fetch(`http://localhost:8000/history/${threadId}`)
      .then((res) => res.json())
      .then((data: HistoryResponse) => { 
        if (data.messages && data.messages.length > 0) {
          
          const formatted: Message[] = data.messages.map((m) => {
            let textContent = "";

            if (typeof m.content === "string") {
              textContent = m.content;
            } 
            else if (typeof m.content === "object" && m.content !== null) {
               if ('text' in m.content) {
                   textContent = (m.content as TextContentObj).text;
               } else {
                   textContent = JSON.stringify(m.content);
               }
            } 
            else {
               textContent = String(m.content);
            }

            return {
              role: m.role === "human" ? "user" : "Nexus",
              content: textContent,
            };
          });

          setMessages(formatted);
        }
      })
      .catch((e) => console.error(e));
  }, [threadId]);

  const upload = async () => {
    if (files.length === 0) return;
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    await fetch("http://localhost:8000/upload", { method: "POST", body: formData });
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFiles(Array.from(e.target.files));
  };

  const handleSend = async () => {
    if (prompt.trim() === "") return;
    const current_prompt = prompt;
    
    setMessages((prev) => [...prev, { role: "user", content: current_prompt }]);
    setPrompt("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            prompt: current_prompt,
            thread_id: threadId || "new" 
        }),
      });

      const data = await res.json();

      if (!threadId || threadId !== data.thread_id) {
        onThreadCreated(data.thread_id);
      }
      setMessages((prev) => [...prev, { role: "Nexus", content: data.response }]);
    } catch (error) {
      console.error("Chat Error:", error);
    }
  };

  return (
    <main className="chat-area">
      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message-wrapper ${msg.role === "user" ? "User" : "Nexus"}`}>
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
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button className="send-btn" onClick={handleSend}>Send</button>
        <div className="upload-controls">
           <input type="file" multiple onChange={handleFile} />
           <button onClick={upload}>Upload</button>
        </div>
      </div>
    </main>
  );
}

export default ChatArea;