import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/axios";
import { PieChart, Pie, Cell } from "recharts";
import { getHistoryAPI } from "../api/services";

export default function Dashboard() {
  const [transactions, setTransactions] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {

      const res = await getHistoryAPI();
      setTransactions(res.data.data);
    };

    fetchHistory();
  }, []);

  const total = transactions.length;
  const fraud = transactions.filter((t) => t.prediction === 1).length;
  const safe = transactions.filter((t) => t.prediction === 0).length;

  const chartData = [
    { name: "Fraud", value: fraud },
    { name: "Safe", value: safe },
  ];

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="flex justify-between mb-6">
        <h1 className="text-2xl font-bold">Dashboard 📊</h1>

        <div>
          <button
            onClick={() => navigate("/")}
            className="bg-blue-500 text-white px-4 py-2 rounded mr-2"
          >
            Home
          </button>

          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded shadow">
          <h2>Total</h2>
          <p className="text-xl font-bold">{total}</p>
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h2>Fraud</h2>
          <p className="text-xl font-bold text-red-500">{fraud}</p>
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h2>Safe</h2>
          <p className="text-xl font-bold text-green-500">{safe}</p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white p-4 rounded shadow mb-6">
        <h2 className="mb-4 font-semibold">Fraud vs Safe</h2>

        <PieChart width={300} height={300}>
          <Pie data={chartData} dataKey="value" outerRadius={100}>
            <Cell />
            <Cell />
          </Pie>
        </PieChart>
      </div>

      {/* History */}
      <div className="bg-white p-4 rounded shadow">
        <h2 className="mb-4 font-semibold">Transaction History</h2>

        {transactions.map((t, i) => (
          <div key={i} className="border-b py-2">
            ₹{t.amount} → {t.prediction === 1 ? "Fraud 🚨" : "Safe ✅"}
          </div>
        ))}
      </div>
    </div>
  );
}
