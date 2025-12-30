import "../App.css";
import { useEffect, useState } from "react";

interface ChatSession {
  id: string;
  title: string;
}

interface SidebarProps {
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  refreshTrigger: number;
}

function SideBar({ onSelectChat, onNewChat, refreshTrigger }: SidebarProps) {
  const [history, setHistory] = useState<ChatSession[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/history")
      .then((res) => {
        if (!res.ok) {
            throw new Error(`Server error: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        // SAFETY CHECK: Only set state if data is actually an array
        if (Array.isArray(data)) {
          setHistory(data);
        } else {
          console.error("Expected array but got:", data);
          setHistory([]); // Fallback to empty list to prevent crash
        }
      })
      .catch((err) => {
        console.error("Failed to load history:", err);
        setHistory([]); // Fallback on error
      });
  }, [refreshTrigger]);

  return (
    <aside className="sidebar">
      <div className="new-chat-section">
        <button className="new-chat-btn" onClick={onNewChat}>
          + New chat
        </button>
      </div>
      <div className="history-section">
        <ul className="history-list">
          {/* SAFETY CHECK: Ensure history exists and is an array before mapping */}
          {Array.isArray(history) && history.map((chat) => (
            <li
              key={chat.id}
              className="history-item"
              onClick={() => onSelectChat(chat.id)}
            >
              {chat.title}
            </li>
          ))}
          
          {/* Optional: Show message if list is empty */}
          {Array.isArray(history) && history.length === 0 && (
            <li style={{ padding: "10px", color: "#666", fontSize: "0.8rem" }}>
              No previous chats
            </li>
          )}
        </ul>
      </div>
    </aside>
  );
}

export default SideBar;