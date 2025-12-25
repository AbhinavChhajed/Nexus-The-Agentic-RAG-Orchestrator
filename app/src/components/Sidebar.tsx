import "../App.css";

function onNewChat() {
  console.log("New chat initiated");
}

function SideBar() {
  return (
    <aside className="sidebar">
      <div className="new-chat-section">
        <button className="new-chat-btn" onClick={onNewChat}>+ New chat</button>
      </div>
      <div className="history-section">
        <ul className="history-list">
          <li className="history-item">React Project Help</li>
          <li className="history-item">Python Script Debug</li>
          <li className="history-item">Meeting Notes</li>
        </ul>
      </div>
    </aside>
  );
}

export default SideBar;