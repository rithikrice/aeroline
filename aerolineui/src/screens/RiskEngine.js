import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from "recharts";

export default function RiskDashboard() {
  const topRiskyData = [
    {
      id: 1,
      identifier: "Flight 123",
      type: "Flight",
      score: 85,
      status: "High Risk",
    },
    {
      id: 2,
      identifier: "Machine A",
      type: "Machine",
      score: 70,
      status: "Medium Risk",
    },
    {
      id: 3,
      identifier: "Flight 456",
      type: "Flight",
      score: 60,
      status: "Medium Risk",
    },
    {
      id: 4,
      identifier: "Machine B",
      type: "Machine",
      score: 55,
      status: "Low Risk",
    },
    {
      id: 5,
      identifier: "Flight 789",
      type: "Flight",
      score: 40,
      status: "Low Risk",
    },
  ];

  const trendData = [
    { day: "Day 1", score: 62 },
    { day: "Day 5", score: 68 },
    { day: "Day 10", score: 72 },
    { day: "Day 15", score: 78 },
    { day: "Day 20", score: 74 },
    { day: "Day 25", score: 80 },
    { day: "Day 30", score: 75 },
  ];

  const riskBreakdown = [
    { name: "High Risk", value: 1 },
    { name: "Medium Risk", value: 2 },
    { name: "Low Risk", value: 2 },
  ];

  const COLORS = ["#ff4d6d", "#ffb347", "#00f5d4"];

  const statusColors = {
    "High Risk": "bg-red-600 text-red-50",
    "Medium Risk": "bg-yellow-600 text-yellow-50",
    "Low Risk": "bg-green-600 text-green-50",
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a192f] to-[#0f223f] text-white p-6 font-sans">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold tracking-wide text-teal-400">
          Unified Risk Dashboard
        </h1>
        <p className="text-gray-300">
          Real-time risk insights for flights and machines
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-10">
        {["Plant", "Lane", "Machine"].map((filter) => (
          <select
            key={filter}
            className="p-2 glass-card rounded-xl text-white border border-gray-700 shadow-md focus:ring-2 focus:ring-teal-400"
          >
            <option>All {filter}s</option>
          </select>
        ))}
      </div>

      {/* Risk Score + Charts */}
      <div className="grid grid-cols-3 gap-8 mb-10 items-center">
        {/* Unified Risk Gauge */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="col-span-1 p-8 rounded-2xl glass-card glass-card-glow flex flex-col items-center"
        >
          <div className="relative w-40 h-40">
            <div className="absolute inset-0 rounded-full border-[10px] border-teal-400/60 flex items-center justify-center">
              <div className="text-center">
                <p className="text-4xl font-bold text-teal-300">75</p>
                <p className="text-gray-400 text-sm">Overall Risk Score</p>
              </div>
            </div>
          </div>
          <div className="flex justify-between w-full mt-8 px-4">
            <div className="text-center">
              <p className="text-gray-400 text-sm">Flight ETA Drift</p>
              <p className="text-xl font-semibold">85</p>
            </div>
            <div className="text-center">
              <p className="text-gray-400 text-sm">Machine Health</p>
              <p className="text-xl font-semibold text-yellow-400">65</p>
            </div>
          </div>
        </motion.div>

        {/* Line Chart */}
        <motion.div
          whileHover={{ scale: 1.01 }}
          className="col-span-1 p-6 rounded-2xl glass-card glass-card-glow"
        >
          <h3 className="text-teal-300 mb-4 font-semibold">
            Risk Trend (30 days)
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f3558" />
              <XAxis dataKey="day" stroke="#aaa" />
              <YAxis stroke="#aaa" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f223f",
                  borderRadius: "10px",
                }}
              />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#00f5d4"
                strokeWidth={3}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Pie Chart */}
        <motion.div
          whileHover={{ scale: 1.01 }}
          className="col-span-1 p-6 rounded-2xl glass-card glass-card-glow"
        >
          <h3 className="text-teal-300 mb-4 font-semibold">Risk Breakdown</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={riskBreakdown}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {riskBreakdown.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f223f",
                  borderRadius: "10px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Top Risky Flights/Machines */}
      <motion.div className="p-6 rounded-2xl glass-card glass-card-glow">
        <h3 className="text-teal-400 font-semibold mb-4 text-lg">
          Top Risky Flights/Machines
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-separate border-spacing-y-2">
            <thead className="text-gray-400">
              <tr>
                <th className="py-2">Identifier</th>
                <th>Type</th>
                <th>Risk Score</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {topRiskyData.map((item) => (
                <tr key={item.id} className="bg-[#112b4a] rounded-lg">
                  <td className="py-3 px-2">{item.identifier}</td>
                  <td>{item.type}</td>
                  <td
                    className={
                      item.score >= 80
                        ? "text-red-400"
                        : item.score >= 60
                        ? "text-yellow-400"
                        : "text-green-400"
                    }
                  >
                    {item.score}
                  </td>
                  <td>
                    <span
                      className={`px-3 py-1 rounded-full text-xs ${
                        statusColors[item.status]
                      }`}
                    >
                      {item.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
