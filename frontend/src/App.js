import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import ProtectedRoute from "./components/ProtectedRoute";

import { useState } from "react";
import API from "./api/axios";

function Home() {
  const [amount, setAmount] = useState("");
  const [result, setResult] = useState(null);

  const handlePredict = async () => {
    try {
      const res = await API.post("/predict", {
        features: [Number(amount)],
      });

      setResult(res.data.data.prediction);
    } catch (error) {
      alert(error.response?.data?.message || "Error");
    }
  };

  // 🔥 STEP 9 (Logout)
  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  return (
    <div>
      <h1>Fraud Detection 🚀</h1>

      {/* INPUT */}
      <input
        type="number"
        placeholder="Enter amount"
        onChange={(e) => setAmount(e.target.value)}
      />

      {/* PREDICT BUTTON */}
      <button onClick={handlePredict}>Predict</button>

      {/* RESULT */}
      {result !== null && (
        <h3>{result === 1 ? "Fraud Detected 🚨" : "Not Fraud ✅"}</h3>
      )}

      {/* LOGOUT BUTTON */}
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
