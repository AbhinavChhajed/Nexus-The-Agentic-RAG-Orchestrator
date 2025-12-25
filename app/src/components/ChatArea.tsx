import "../App.css";

function ChatArea() {
  return (
    <main className="chat-area">
      <div className="messages-container">
        <div className="message-wrapper">
          <strong className="message-sender">Nexus:</strong>
          <p className="message-text">Hello. I am ready to help.</p>
        </div>
      </div>

      <div className="input-section">
        <input className="chat-input" type="text" placeholder="Send a message..." />
        <button className="send-btn">Send</button>
      </div>
    </main>
  );
}

export default ChatArea;