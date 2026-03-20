import { useState } from "react";
import axios from "axios";

function App() {
  const [amount, setAmount] = useState("");
  const [result, setResult] = useState(null);

  const handlePredict = async () => {
    try {
      const res = await axios.post("http://localhost:5000/api/predict", {
        features: [Number(amount)],
      });

      setResult(res.data.prediction);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Fraud Detection System</h2>

      <input
        type="number"
        placeholder="Enter amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />

      <button onClick={handlePredict}>Predict</button>

      {result !== null && (
        <h3>{result === 1 ? "🚨 Fraud Detected" : "✅ Legit Transaction"}</h3>
      )}
    </div>
  );
}

export default App;
