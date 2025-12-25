import "./App.css";
import SideBar from "./components/Sidebar";
import ChatArea from "./components/Chatarea";

function App() {
  return (
    <div className="app-layout">
      <SideBar />
      <ChatArea />
    </div>
  );
}

export default App;