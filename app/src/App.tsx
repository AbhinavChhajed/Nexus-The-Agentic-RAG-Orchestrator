import { useState } from "react";
import SideBar from "./components/Sidebar"; // Adjust path as needed
import ChatArea from "./components/ChatArea"; // Adjust path as needed
import "./App.css";

function App() {
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [refreshSidebar, setRefreshSidebar] = useState(0);

  const handleNewChat = () => {
    setActiveThreadId(null);
  };

  const handleThreadCreated = (newId: string) => {
    setActiveThreadId(newId);
    setRefreshSidebar((prev) => prev + 1);
  };

  return (
    <div className="app-container">
      <SideBar 
        onSelectChat={setActiveThreadId} 
        onNewChat={handleNewChat} 
        refreshTrigger={refreshSidebar}
      />
      
      {/* CRITICAL FIX: 
         key={activeThreadId} ensures ChatArea is re-mounted cleanly 
         on every chat switch. 
      */}
      <ChatArea 
        key={activeThreadId || "new"} 
        threadId={activeThreadId} 
        onThreadCreated={handleThreadCreated} 
      />
    </div>
  );
}

export default App;