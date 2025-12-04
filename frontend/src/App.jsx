import { useState } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");

  const callBackend = async () => {
    try {
      const res = await axios.get("http://localhost:8000/");
      setMessage(res.data.message);
    } catch (err) {
      setMessage("Error connecting to backend");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Smart Campus Assistant - Day 1</h1>
      <button onClick={callBackend}>Call Backend</button>
      <p>{message}</p>
    </div>
  );
}

export default App;
