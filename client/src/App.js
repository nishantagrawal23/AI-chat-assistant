import Chat from "./chat";
import Upload from "./upload";
import { useState } from "react";
import "./styles.css";

function App() {
    const [isUploaded, setIsUploaded] = useState(false);
  return (
      <div className="app">
      <div className="header">💬 Resume Chat AI Assistant</div>
      <Upload setIsUploaded={setIsUploaded} />
      <Chat isUploaded={isUploaded} />
    </div>
  );
}

export default App;