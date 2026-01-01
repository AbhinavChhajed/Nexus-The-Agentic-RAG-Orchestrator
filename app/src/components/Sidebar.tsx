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
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/history")
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        if (Array.isArray(data)) setHistory(data);
      })
      .catch(() => setHistory([]));
  }, [refreshTrigger]);

  const handleDoubleClick = (chat: ChatSession) => {
    setEditingId(chat.id);
    setEditValue(chat.title);
  };

  const handleRename = async () => {
    if (!editingId || !editValue.trim()) {
      setEditingId(null);
      return;
    }

    setHistory((prev) =>
      prev.map((chat) =>
        chat.id === editingId ? { ...chat, title: editValue } : chat
      )
    );

    await fetch("http://localhost:8000/rename", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ thread_id: editingId, title: editValue }),
    });

    setEditingId(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleRename();
    if (e.key === "Escape") setEditingId(null);
  };

  return (
    <aside className="sidebar">
      <div className="new-chat-section">
        <button className="new-chat-btn" onClick={onNewChat}>
          + New chat
        </button>
      </div>
      <div className="history-section">
        <ul className="history-list">
          {Array.isArray(history) &&
            history.map((chat) => (
              <li
                key={chat.id}
                className="history-item"
                onClick={() => onSelectChat(chat.id)}
                onDoubleClick={() => handleDoubleClick(chat)}
              >
                {editingId === chat.id ? (
                  <input
                    type="text"
                    autoFocus
                    className="rename-input"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onBlur={handleRename}
                    onKeyDown={handleKeyDown}
                  />
                ) : (
                  <span>{chat.title}</span>
                )}
              </li>
            ))}
        </ul>
      </div>
    </aside>
  );
}

export default SideBar;
