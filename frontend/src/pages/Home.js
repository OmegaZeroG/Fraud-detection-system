import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/axios";

export default function Home() {
  const [amount, setAmount] = useState("");
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const handlePredict = async () => {
    if (!amount) {
      alert("Enter amount");
      return;
    }

    try {
      const res = await API.post("/predict", {
        features: [Number(amount)],
      });

      setResult(res.data.data.prediction);
    } catch (error) {
      alert("Prediction failed");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      <div className="bg-white p-8 rounded-2xl shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6 text-center">
          Fraud Detection 🚀
        </h1>

        <input
          type="number"
          placeholder="Enter amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="w-full p-2 border rounded mb-4"
        />

        <button
          onClick={handlePredict}
          className="w-full bg-blue-500 text-white p-2 rounded mb-3 hover:bg-blue-600"
        >
          Predict
        </button>

        <button
          onClick={() => navigate("/dashboard")}
          className="w-full bg-green-500 text-white p-2 rounded mb-3 hover:bg-green-600"
        >
          Go to Dashboard 📊
        </button>

        {result !== null && (
          <div className="text-center mt-4 font-semibold">
            {result === 1 ? "Fraud Detected 🚨" : "Not Fraud ✅"}
          </div>
        )}

        <button
          onClick={handleLogout}
          className="w-full bg-red-500 text-white p-2 rounded mt-4 hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
