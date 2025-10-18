// import { motion } from "framer-motion";
// import React, { useState, useEffect } from "react";
// import { Bar } from "react-chartjs-2";
// import {
//   Chart as ChartJS,
//   CategoryScale,
//   LinearScale,
//   BarElement,
//   Title,
//   Tooltip,
//   Legend,
// } from "chart.js";
// import {
//   LineChart,
//   Line,
//   XAxis,
//   YAxis,
//   Tooltip as RechartsTooltip,
//   ResponsiveContainer,
//   CartesianGrid,
//   PieChart,
//   Pie,
//   Cell,
// } from "recharts";

// ChartJS.register(
//   CategoryScale,
//   LinearScale,
//   BarElement,
//   Title,
//   Tooltip,
//   Legend
// );

// // ------------------ MOCK DATA ------------------

// const MOCK_FACTORIES = ["Factory A", "Factory B", "Factory C"];
// const MOCK_ASSIGNMENTS = ["Unassigned", "Ops Team 1", "Ops Team 2"];

// const MOCK_RISKS = [
//   {
//     id: "risk-1",
//     type: "Flight",
//     flightId: "OS123",
//     machineId: "M-234",
//     severity: "high",
//     priority: "urgent",
//     factory: "Factory A",
//     assignment: "Ops Team 1",
//     riskScore: 0.92,
//     suggestedAction: "Expedite flight OS123",
//     roi: "3.2x",
//     lastUpdated: "2025-10-12 14:32",
//     topFeatures: [
//       "ETA Drift",
//       "Temperature Spike",
//       "Load Delay",
//       "Spare Lead Time",
//       "Machine Health",
//     ],
//     cortexNarrative:
//       "Flight OS123 is at high risk due to ETA drift and machine anomalies at Factory A.",
//     timelineEvents: [
//       { time: "08:00", event: "Flight Departed" },
//       { time: "10:15", event: "Machine Temp Spike" },
//       { time: "11:30", event: "ETA Drift Detected" },
//     ],
//   },
//   {
//     id: "risk-2",
//     type: "Machine",
//     flightId: "OS124",
//     machineId: "M-235",
//     severity: "medium",
//     priority: "normal",
//     factory: "Factory B",
//     assignment: "Ops Team 2",
//     riskScore: 0.65,
//     suggestedAction: "Pull spare M-235",
//     roi: "1.8x",
//     lastUpdated: "2025-10-12 13:50",
//     topFeatures: [
//       "ETA Drift",
//       "Spare Inventory",
//       "Vibration Alert",
//       "Job Congestion",
//       "Temperature",
//     ],
//     cortexNarrative:
//       "Flight OS124 shows moderate risk due to spare inventory shortage and vibration alerts.",
//     timelineEvents: [
//       { time: "09:00", event: "Flight Departed" },
//       { time: "10:45", event: "Vibration Alert" },
//     ],
//   },
//   // Additional mock risks for demo
//   {
//     id: "risk-3",
//     type: "Flight",
//     flightId: "OS125",
//     machineId: "M-236",
//     severity: "low",
//     priority: "normal",
//     factory: "Factory C",
//     assignment: "Unassigned",
//     riskScore: 0.38,
//     suggestedAction: "Monitor flight OS125",
//     roi: "1.2x",
//     lastUpdated: "2025-10-12 12:20",
//     topFeatures: ["ETA Drift", "Load Delay", "Inventory Level"],
//     cortexNarrative: "Flight OS125 is low risk; no immediate action required.",
//     timelineEvents: [{ time: "07:00", event: "Flight Departed" }],
//   },
// ];

// // Trend data for line chart
// const trendData = Array.from({ length: 30 }, (_, i) => ({
//   day: `Day ${i + 1}`,
//   score: Math.floor(Math.random() * 40) + 50,
// }));

// // Risk breakdown pie chart
// const riskBreakdown = [
//   {
//     name: "High Risk",
//     value: MOCK_RISKS.filter((r) => r.severity === "high").length,
//   },
//   {
//     name: "Medium Risk",
//     value: MOCK_RISKS.filter((r) => r.severity === "medium").length,
//   },
//   {
//     name: "Low Risk",
//     value: MOCK_RISKS.filter((r) => r.severity === "low").length,
//   },
// ];

// const COLORS = ["#ff4d6d", "#ffb347", "#00f5d4"];
// const statusColors = {
//   "High Risk": "bg-red-600 text-red-50",
//   "Medium Risk": "bg-yellow-600 text-yellow-50",
//   "Low Risk": "bg-green-600 text-green-50",
// };

// const topRiskyData = [
//   {
//     id: 1,
//     identifier: "Flight 123",
//     type: "Flight",
//     score: 85,
//     status: "High Risk",
//   },
//   {
//     id: 2,
//     identifier: "Machine A",
//     type: "Machine",
//     score: 70,
//     status: "Medium Risk",
//   },
//   {
//     id: 3,
//     identifier: "Flight 456",
//     type: "Flight",
//     score: 60,
//     status: "Medium Risk",
//   },
//   {
//     id: 4,
//     identifier: "Machine B",
//     type: "Machine",
//     score: 55,
//     status: "Low Risk",
//   },
//   {
//     id: 5,
//     identifier: "Flight 789",
//     type: "Flight",
//     score: 40,
//     status: "Low Risk",
//   },
// ];

// // ------------------ DASHBOARD COMPONENT ------------------

// export default function UnifiedRiskDashboard() {
//   const [selectedRisk, setSelectedRisk] = useState(null);
//   // const [overallRiskScore, setOverallRiskScore] = useState(
//   //   MOCK_RISKS.reduce((acc, r) => acc + r.riskScore, 0) / MOCK_RISKS.length
//   // );
//   // const [flightEtaDrift, setFlightEtaDrift] = useState(0);
//   // const [machineHealth, setMachineHealth] = useState(0);
//   const [overallRiskScore, setOverallRiskScore] = useState(78); // Example risk score
//   const [flightEtaDrift, setFlightEtaDrift] = useState(15); // Example ETA drift in minutes
//   const [machineHealth, setMachineHealth] = useState(82); // Example machine health percentage

//   // Add useEffect to fetch data from backend
//   useEffect(() => {
//     const fetchMetrics = async () => {
//       try {
//         // Replace with your actual API endpoint
//         const response = await fetch("/api/metrics");
//         const data = await response.json();

//         setOverallRiskScore(data.overallRiskScore);
//         setFlightEtaDrift(data.flightEtaDrift);
//         setMachineHealth(data.machineHealth);
//       } catch (error) {
//         console.error("Failed to fetch metrics:", error);
//         // Set default values or handle error
//         setOverallRiskScore(0);
//         setFlightEtaDrift(0);
//         setMachineHealth(0);
//       }
//     };

//     fetchMetrics();
//   }, []); // Empty dependency array means this runs once on component mount
//   const [filters, setFilters] = useState({
//     severity: "all",
//     factory: "all",
//     assignment: "all",
//   });
//   const [showModal, setShowModal] = useState(false);

//   const filteredRisks = MOCK_RISKS.filter(
//     (r) =>
//       (filters.severity === "all" || r.severity === filters.severity) &&
//       (filters.factory === "all" || r.factory === filters.factory) &&
//       (filters.assignment === "all" || r.assignment === filters.assignment)
//   );

//   const getBarData = (features) => ({
//     labels: features,
//     datasets: [
//       {
//         label: "Feature Impact",
//         data: features.map(() => Math.random() * 1),
//         backgroundColor: "rgba(16, 185, 129, 0.7)",
//       },
//     ],
//   });

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-[#0a192f] to-[#0f223f] text-white p-6 font-sans">
//       {/* Header */}
//       <div className="flex justify-between items-center mb-6">
//         <h1 className="text-3xl font-bold tracking-wide text-teal-400">
//           Unified Risk Dashboard
//         </h1>
//         <p className="text-gray-300">
//           Real-time risk insights for Flights and Machines
//         </p>
//       </div>

//       {/* Top Summary Cards */}
//       <div className="grid grid-cols-3 gap-8 mb-10">
//         {/* Overall Risk Gauge */}
//         <motion.div
//           whileHover={{ scale: 1.02 }}
//           className="col-span-1 p-8 rounded-2xl glass-card glass-card-glow flex flex-col items-center"
//         >
//           <div className="relative w-40 h-40">
//             <div
//               className={`absolute inset-0 rounded-full border-[10px] flex items-center justify-center ${
//                 overallRiskScore > 85
//                   ? "border-red-500/60"
//                   : overallRiskScore > 65
//                   ? "border-orange-500/60"
//                   : overallRiskScore > 45
//                   ? "border-yellow-500/60"
//                   : "border-green-500/60"
//               }`}
//             >
//               <div className="text-center">
//                 <p
//                   className={`text-4xl font-bold ${
//                     overallRiskScore > 85
//                       ? "text-red-400"
//                       : overallRiskScore > 65
//                       ? "text-orange-400"
//                       : overallRiskScore > 45
//                       ? "text-yellow-400"
//                       : "text-green-400"
//                   }`}
//                 >
//                   {overallRiskScore}
//                 </p>
//                 <p className="text-gray-400 text-sm">Overall Risk Score</p>
//               </div>
//             </div>
//           </div>
//           <div className="flex justify-between w-full mt-8 px-4">
//             <div className="text-center">
//               <p className="text-gray-400 text-sm">Flight ETA Drift</p>
//               <p className="text-xl font-semibold">{flightEtaDrift}</p>
//             </div>
//             <div className="text-center">
//               <p className="text-gray-400 text-sm">Machine Health</p>
//               <p className="text-xl font-semibold">{machineHealth}</p>
//             </div>
//           </div>
//         </motion.div>

//         {/* Risk Trend Line */}
//         <motion.div
//           whileHover={{ scale: 1.01 }}
//           className="col-span-1 p-6 rounded-2xl glass-card glass-card-glow"
//         >
//           <h3 className="text-teal-300 mb-4 font-semibold">
//             Risk Trend (30 days)
//           </h3>
//           <ResponsiveContainer width="100%" height={200}>
//             <LineChart data={trendData}>
//               <CartesianGrid strokeDasharray="3 3" stroke="#1f3558" />
//               <XAxis dataKey="day" stroke="#aaa" />
//               <YAxis stroke="#aaa" />
//               <RechartsTooltip
//                 contentStyle={{
//                   backgroundColor: "#0f223f",
//                   borderRadius: "10px",
//                 }}
//               />
//               <Line
//                 type="monotone"
//                 dataKey="score"
//                 stroke="#00f5d4"
//                 strokeWidth={3}
//                 dot={false}
//               />
//             </LineChart>
//           </ResponsiveContainer>
//         </motion.div>

//         {/* Risk Breakdown Pie */}
//         <motion.div
//           whileHover={{ scale: 1.01 }}
//           className="col-span-1 p-6 rounded-2xl glass-card glass-card-glow"
//         >
//           <h3 className="text-teal-300 mb-4 font-semibold">Risk Breakdown</h3>
//           <ResponsiveContainer width="100%" height={200}>
//             <PieChart>
//               <Pie
//                 data={riskBreakdown}
//                 cx="50%"
//                 cy="50%"
//                 outerRadius={80}
//                 dataKey="value"
//                 labelLine={false}
//               >
//                 {riskBreakdown.map((entry, index) => (
//                   <Cell
//                     key={`cell-${index}`}
//                     fill={COLORS[index % COLORS.length]}
//                   />
//                 ))}
//               </Pie>
//               <RechartsTooltip
//                 contentStyle={{
//                   backgroundColor: "#0f223f",
//                   borderRadius: "10px",
//                 }}
//               />
//             </PieChart>
//           </ResponsiveContainer>
//         </motion.div>
//       </div>

//       {/* Filters */}
//       <div className="flex gap-4 mb-8">
//         <select
//           className="p-2 glass-card rounded-xl text-white border border-gray-700 shadow-md focus:ring-2 focus:ring-teal-400"
//           value={filters.severity}
//           onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
//         >
//           <option value="all">All Severities</option>
//           <option value="high">High</option>
//           <option value="medium">Medium</option>
//           <option value="low">Low</option>
//         </select>
//         <select
//           className="p-2 glass-card rounded-xl text-white border border-gray-700 shadow-md focus:ring-2 focus:ring-teal-400"
//           value={filters.factory}
//           onChange={(e) => setFilters({ ...filters, factory: e.target.value })}
//         >
//           <option value="all">All Factories</option>
//           {MOCK_FACTORIES.map((f) => (
//             <option key={f} value={f}>
//               {f}
//             </option>
//           ))}
//         </select>
//         <select
//           className="p-2 glass-card rounded-xl text-white border border-gray-700 shadow-md focus:ring-2 focus:ring-teal-400"
//           value={filters.assignment}
//           onChange={(e) =>
//             setFilters({ ...filters, assignment: e.target.value })
//           }
//         >
//           <option value="all">All Teams</option>
//           {MOCK_ASSIGNMENTS.map((a) => (
//             <option key={a} value={a}>
//               {a}
//             </option>
//           ))}
//         </select>
//       </div>
//       {/* Risk Cards Grid */}
//       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
//         {filteredRisks.map((risk) => (
//           <motion.div
//             key={risk.id}
//             whileHover={{ scale: 1.03 }}
//             className="p-4 bg-[#112b4a] rounded-2xl shadow cursor-pointer flex flex-col"
//           >
//             <div className="flex justify-between items-center mb-2">
//               <div>
//                 <p className="text-sm text-gray-400">{risk.flightId}</p>
//                 <p className="text-xs text-gray-500">{risk.machineId}</p>
//                 <p className="text-xs text-gray-400">
//                   {risk.priority.toUpperCase()}
//                 </p>
//               </div>
//               <span
//                 className={`px-2 py-1 text-xs rounded font-semibold ${
//                   risk.severity === "high"
//                     ? "bg-rose-500"
//                     : risk.severity === "medium"
//                     ? "bg-amber-400"
//                     : "bg-green-500"
//                 }`}
//               >
//                 {risk.severity.toUpperCase()}
//               </span>
//             </div>

//             <div className="h-24 bg-black/40 rounded mb-2 flex items-center justify-center text-slate-400 text-xs">
//               Mini Map
//             </div>

//             <div className="mb-2">
//               <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
//                 <div
//                   className={`h-2 rounded-full ${
//                     risk.riskScore > 0.7
//                       ? "bg-rose-500"
//                       : risk.riskScore > 0.4
//                       ? "bg-amber-400"
//                       : "bg-green-500"
//                   }`}
//                   style={{ width: `${risk.riskScore * 100}%` }}
//                 ></div>
//               </div>
//               <p className="text-xs text-gray-400 mt-1">
//                 Risk Score: {(risk.riskScore * 100).toFixed(0)}%
//               </p>
//             </div>

//             <h3 className="text-sm font-semibold">{risk.suggestedAction}</h3>
//             <p className="text-xs text-gray-400 mb-2">ROI: {risk.roi}</p>

//             <div className="flex gap-2 mt-auto">
//               <button
//                 className="flex-1 bg-emerald-600 px-2 py-1 rounded text-xs hover:bg-emerald-500"
//                 onClick={() => setShowModal(true)}
//               >
//                 Apply
//               </button>
//               <button
//                 className="flex-1 bg-slate-700 px-2 py-1 rounded text-xs hover:bg-slate-600"
//                 onClick={() => alert(`Simulate ${risk.suggestedAction}`)}
//               >
//                 Simulate
//               </button>
//               <button
//                 className="flex-1 bg-cyan-600 px-2 py-1 rounded text-xs hover:bg-cyan-500"
//                 onClick={() => setSelectedRisk(risk)}
//               >
//                 Open
//               </button>
//             </div>
//           </motion.div>
//         ))}
//       </div>

//       {/* Slide-over Detail */}
//       {selectedRisk && (
//         <aside className="fixed right-0 top-0 w-96 h-full p-6 bg-[#112b4a] rounded-l-2xl shadow-lg flex flex-col overflow-y-auto z-40">
//           <div className="flex justify-between items-center mb-4">
//             <h2 className="text-xl font-semibold">
//               {selectedRisk.suggestedAction}
//             </h2>
//             <button onClick={() => setSelectedRisk(null)}>✕</button>
//           </div>

//           <p className="text-sm text-gray-400 mb-1">
//             Flight: {selectedRisk.flightId}
//           </p>
//           <p className="text-sm text-gray-400 mb-1">
//             Machine: {selectedRisk.machineId}
//           </p>
//           <p className="text-sm text-gray-400 mb-1">
//             Severity: {selectedRisk.severity}
//           </p>
//           <p className="text-sm text-gray-400 mb-1">
//             Last Updated: {selectedRisk.lastUpdated}
//           </p>

//           <div className="h-36 bg-black/40 rounded mb-2 flex items-center justify-center text-slate-400 text-xs">
//             Flight / Machine Map
//           </div>

//           <div className="mb-4">
//             <h4 className="text-sm font-semibold mb-2">Timeline</h4>
//             <ul className="text-xs text-gray-400 space-y-1">
//               {selectedRisk.timelineEvents.map((e, i) => (
//                 <li key={i}>
//                   <span className="font-semibold">{e.time}</span> - {e.event}
//                 </li>
//               ))}
//             </ul>
//           </div>

//           <div className="mb-4">
//             <h4 className="text-sm font-semibold mb-2">Explainability</h4>
//             <Bar
//               data={getBarData(selectedRisk.topFeatures)}
//               options={{ plugins: { legend: { display: false } } }}
//             />
//             <p className="text-xs text-gray-400 mt-2">
//               {selectedRisk.cortexNarrative}
//             </p>
//           </div>

//           <div className="mb-4">
//             <h4 className="text-sm font-semibold mb-2">Action Panel</h4>
//             <p className="text-xs text-gray-400 mb-1">
//               Recommended: {selectedRisk.suggestedAction}
//             </p>
//             <p className="text-xs text-gray-400 mb-1">
//               ROI: {selectedRisk.roi}
//             </p>
//             <p className="text-xs text-gray-400 mb-1">
//               Alternative: Monitor flight / Pull spare
//             </p>
//           </div>

//           <div className="mb-4">
//             <h4 className="text-sm font-semibold mb-2">Comments & Audit</h4>
//             <textarea
//               className="w-full p-2 rounded bg-slate-800 text-sm mb-2"
//               placeholder="Add comment..."
//             ></textarea>
//             <button
//               className="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-xs"
//               onClick={() => alert("POST comment / audit")}
//             >
//               Add Comment
//             </button>
//           </div>

//           <div className="mt-auto flex gap-3">
//             <button
//               className="flex-1 bg-emerald-600 px-3 py-2 rounded hover:bg-emerald-500"
//               onClick={() => setShowModal(true)}
//             >
//               Apply Action
//             </button>
//             <button
//               className="flex-1 bg-slate-700 px-3 py-2 rounded hover:bg-slate-600"
//               onClick={() => alert("Simulate Action")}
//             >
//               Simulate
//             </button>
//           </div>
//         </aside>
//       )}

//       {/* Modal: Apply Action */}
//       {showModal && (
//         <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
//           <div className="bg-[#112b4a] p-6 rounded-2xl w-96 shadow-lg">
//             <h3 className="text-lg font-semibold mb-4">Confirm Apply Action</h3>
//             <p className="text-sm text-gray-400 mb-4">
//               Applying this action may incur costs. ROI: {selectedRisk?.roi}
//             </p>
//             <div className="flex gap-3">
//               <button
//                 className="flex-1 bg-emerald-600 px-3 py-2 rounded hover:bg-emerald-500"
//                 onClick={() => {
//                   setShowModal(false);
//                   alert("Action applied! Webhook triggered.");
//                 }}
//               >
//                 Confirm
//               </button>
//               <button
//                 className="flex-1 bg-slate-700 px-3 py-2 rounded hover:bg-slate-600"
//                 onClick={() => setShowModal(false)}
//               >
//                 Cancel
//               </button>
//             </div>
//           </div>
//         </div>
//       )}

//       {/* Top Risky Flights/Machines */}
//       <motion.div className="p-6 rounded-2xl glass-card glass-card-glow">
//         <h3 className="text-teal-400 font-semibold mb-4 text-lg">
//           Top Risky Flights/Machines
//         </h3>
//         <div className="overflow-x-auto">
//           <table className="w-full text-left border-separate border-spacing-y-2">
//             <thead className="text-gray-400">
//               <tr>
//                 <th className="py-2">Identifier</th>
//                 <th>Type</th>
//                 <th>Risk Score</th>
//                 <th>Status</th>
//               </tr>
//             </thead>
//             <tbody>
//               {topRiskyData.map((item) => (
//                 <tr key={item.id} className="bg-[#112b4a] rounded-lg">
//                   <td className="py-3 px-2">{item.identifier}</td>
//                   <td>{item.type}</td>
//                   <td
//                     className={
//                       item.score >= 80
//                         ? "text-red-400"
//                         : item.score >= 60
//                         ? "text-yellow-400"
//                         : "text-green-400"
//                     }
//                   >
//                     {item.score}
//                   </td>
//                   <td>
//                     <span
//                       className={`px-3 py-1 rounded-full text-xs ${
//                         statusColors[item.status]
//                       }`}
//                     >
//                       {item.status}
//                     </span>
//                   </td>
//                 </tr>
//               ))}
//             </tbody>
//           </table>
//         </div>
//       </motion.div>
//     </div>
//   );
// }

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from "recharts";

import { RISKS, RISK_SEVERITY, FACILITIES, TEAMS, PERFORMANCE_HISTORY, FLIGHTS, MACHINES, AIRPORTS } from "../data/mockData";
import PanicButton from "../components/PanicButton";
import { MapContainer, TileLayer, Polyline, Marker } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// ------------------ PREPARE DATA FROM MOCK DATA ------------------
const MOCK_FACTORIES = Object.values(FACILITIES).map(f => f.name);
const MOCK_ASSIGNMENTS = ["Unassigned", ...TEAMS.map(t => t.name)];

const MOCK_RISKS = RISKS.map(risk => ({
  id: risk.id,
  type: risk.type,
  flightId: risk.flightId,
  machineId: risk.machineId,
  severity: risk.severity,
  priority: risk.priority,
  factory: FACILITIES[risk.facility]?.name || "Unknown Facility",
  assignment: risk.assignment,
  riskScore: risk.riskScore,
  suggestedAction: risk.suggestedAction,
  roi: risk.roi,
  lastUpdated: risk.detectedAt,
  topFeatures: risk.topFeatures,
  cortexNarrative: risk.cortexNarrative,
  timelineEvents: risk.timeline.map(t => ({ time: t.time, event: t.event })),
}));

// Generate actual dates for the last 30 days
const generateLast30Days = () => {
  const dates = [];
  const today = new Date();
  for (let i = 29; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
  }
  return dates;
};

const last30DayDates = generateLast30Days();

const trendData = PERFORMANCE_HISTORY.last30Days.riskScore.map((score, i) => ({
  day: last30DayDates[i],
  score: score,
}));

const riskBreakdown = [
  {
    name: "High Risk",
    value: RISKS.filter((r) => r.severity === RISK_SEVERITY.HIGH || r.severity === RISK_SEVERITY.CRITICAL).length,
  },
  {
    name: "Medium Risk",
    value: RISKS.filter((r) => r.severity === RISK_SEVERITY.MEDIUM).length,
  },
  {
    name: "Low Risk",
    value: RISKS.filter((r) => r.severity === RISK_SEVERITY.LOW).length,
  },
];

const COLORS = ["#ff4d6d", "#ffb347", "#00f5d4"];
const statusColors = {
  "High Risk": "bg-red-600 text-red-50",
  "Medium Risk": "bg-yellow-600 text-yellow-50",
  "Low Risk": "bg-green-600 text-green-50",
};

// Generate top risky items from real data
const topRiskyData = [
  ...FLIGHTS.filter(f => f.status === 'critical' || f.status === 'delayed').map(f => ({
    id: f.id,
    identifier: f.flightNumber,
    type: "Flight",
    score: Math.round((Math.abs(f.etaDrift) + 50) * 1.5),
    status: Math.abs(f.etaDrift) > 30 ? "High Risk" : Math.abs(f.etaDrift) > 10 ? "Medium Risk" : "Low Risk",
  })),
  ...MACHINES.filter(m => m.health < 90).map(m => ({
    id: m.id,
    identifier: m.id,
    type: "Machine",
    score: m.health,
    status: m.health < 70 ? "High Risk" : m.health < 85 ? "Medium Risk" : "Low Risk",
  }))
].sort((a, b) => b.score - a.score).slice(0, 8);

// ------------------ DASHBOARD COMPONENT ------------------
export default function UnifiedRiskDashboard() {
  const [selectedRisk, setSelectedRisk] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [filters, setFilters] = useState({
    severity: "all",
    factory: "all",
    assignment: "all",
  });
  const [tableFilters, setTableFilters] = useState({
    type: "all",
    status: "all",
    sortBy: "desc",
  });

  // Calculate real-time metrics from data
  const avgRiskScore = Math.round(PERFORMANCE_HISTORY.last30Days.riskScore.slice(-7).reduce((a, b) => a + b, 0) / 7);
  const avgFlightDrift = Math.round(FLIGHTS.reduce((sum, f) => sum + Math.abs(f.etaDrift), 0) / FLIGHTS.length);
  const avgMachineHealth = Math.round(MACHINES.reduce((sum, m) => sum + m.health, 0) / MACHINES.length);

  const [overallRiskScore, setOverallRiskScore] = useState(avgRiskScore); // 0-100
  const [flightEtaDrift, setFlightEtaDrift] = useState(avgFlightDrift); // minutes
  const [machineHealth, setMachineHealth] = useState(avgMachineHealth); // percentage

  const normalizedOverallRisk = overallRiskScore / 100;

  const filteredRisks = MOCK_RISKS.filter(
    (r) =>
      (filters.severity === "all" || r.severity === filters.severity) &&
      (filters.factory === "all" || r.factory === filters.factory) &&
      (filters.assignment === "all" || r.assignment === filters.assignment)
  );

  const getBarData = (features) => ({
    labels: features,
    datasets: [
      {
        label: "Feature Impact",
        data: features.map(() => Math.floor(Math.random() * 20) + 10),
        backgroundColor: "#10b981aa",
      },
    ],
  });

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6 font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-wide text-teal-400 mb-2">
            Unified Risk Dashboard
          </h1>
          <p className="text-gray-300 text-sm md:text-base">
            Real-time risk insights for Flights and Machines
          </p>
        </div>
        <PanicButton variant="default" />
      </div>

      {/* Top Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {/* Overall Risk */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="p-6 rounded-2xl glass-card glass-card-glow flex flex-col items-center"
        >
          <div className="relative w-36 h-36">
            <div
              className={`absolute inset-0 rounded-full border-[10px] flex items-center justify-center ${
                normalizedOverallRisk > 0.85
                  ? "border-red-500/60"
                  : normalizedOverallRisk > 0.65
                  ? "border-orange-500/60"
                  : normalizedOverallRisk > 0.45
                  ? "border-yellow-500/60"
                  : "border-green-500/60"
              }`}
            >
              <div className="text-center">
                <p
                  className={`text-4xl font-bold ${
                    normalizedOverallRisk > 0.85
                      ? "text-red-400"
                      : normalizedOverallRisk > 0.65
                      ? "text-orange-400"
                      : normalizedOverallRisk > 0.45
                      ? "text-yellow-400"
                      : "text-green-400"
                  }`}
                >
                  {overallRiskScore}
                </p>
                <p className="text-gray-400 text-sm">Overall Risk Score</p>
              </div>
            </div>
          </div>
          <div className="flex justify-between w-full mt-6 px-4">
            <div className="text-center">
              <p className="text-gray-400 text-sm">Flight ETA Drift</p>
              <p className="text-xl font-semibold">{flightEtaDrift} min</p>
            </div>
            <div className="text-center">
              <p className="text-gray-400 text-sm">Machine Health</p>
              <p className="text-xl font-semibold">{machineHealth}%</p>
            </div>
          </div>
        </motion.div>

        {/* Risk Trend */}
        <motion.div
          whileHover={{ scale: 1.01 }}
          className="p-6 rounded-2xl glass-card glass-card-glow"
        >
          <h3 className="text-teal-300 mb-4 font-semibold">
            Risk Trend (30 days)
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f3558" />
              <XAxis dataKey="day" stroke="#aaa" />
              <YAxis stroke="#aaa" />
              <RechartsTooltip
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

        {/* Risk Breakdown */}
        <motion.div
          whileHover={{ scale: 1.01 }}
          className="p-6 rounded-2xl glass-card glass-card-glow"
        >
          <h3 className="text-teal-300 mb-4 font-semibold">Risk Breakdown</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={riskBreakdown}
                cx="50%"
                cy="45%"
                outerRadius={70}
                dataKey="value"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                labelLine={true}
              >
                {riskBreakdown.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: "#0f223f",
                  borderRadius: "10px",
                  border: "1px solid #14b8a6",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-2 text-xs">
            {riskBreakdown.map((entry, index) => (
              <div key={entry.name} className="flex items-center gap-1">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index] }}></div>
                <span className="text-gray-400">{entry.name} ({entry.value})</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-8">
        <select
          className="p-2 glass-card rounded-xl text-white border border-gray-700 shadow-md focus:ring-2 focus:ring-teal-400"
          value={filters.severity}
          onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
        >
          <option value="all">All Severities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select
          className="p-2 glass-card rounded-xl text-white border border-gray-700 shadow-md focus:ring-2 focus:ring-teal-400"
          value={filters.factory}
          onChange={(e) => setFilters({ ...filters, factory: e.target.value })}
        >
          <option value="all">All Factories</option>
          {MOCK_FACTORIES.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
        <select
          className="p-2 glass-card rounded-xl text-white border border-gray-700 shadow-md focus:ring-2 focus:ring-teal-400"
          value={filters.assignment}
          onChange={(e) =>
            setFilters({ ...filters, assignment: e.target.value })
          }
        >
          <option value="all">All Teams</option>
          {MOCK_ASSIGNMENTS.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </div>

      {/* Risk Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
        {filteredRisks.map((risk) => (
          <motion.div
            key={risk.id}
            whileHover={{ scale: 1.03 }}
            className="p-4 bg-[#112b4a] rounded-2xl shadow cursor-pointer flex flex-col hover:shadow-2xl transition"
          >
            <div className="flex justify-between items-center mb-2">
              <div>
                <p className="text-sm text-gray-400">{risk.flightId}</p>
                <p className="text-xs text-gray-500">{risk.machineId}</p>
                <p className="text-xs text-gray-400">
                  {risk.priority.toUpperCase()}
                </p>
              </div>
              <div className="relative">
                <span
                  className={`px-2 py-1 text-xs rounded font-semibold ${
                    risk.severity === "high" || risk.severity === "critical"
                      ? "bg-rose-500 pulse-critical"
                      : risk.severity === "medium"
                      ? "bg-amber-400"
                      : "bg-green-500"
                  }`}
                >
                  {risk.severity.toUpperCase()}
                </span>
                {(risk.severity === "high" || risk.severity === "critical") && (
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full pulse-critical"></div>
                )}
              </div>
            </div>

            <div className="h-24 bg-black/40 rounded mb-2 overflow-hidden relative">
              {risk.flightId ? (
                (() => {
                  const flight = FLIGHTS.find(f => f.id === risk.flightId);
                  if (flight && flight.route && flight.route.length > 1) {
                    // Calculate center point of route
                    const midLat = (flight.route[0][0] + flight.route[flight.route.length - 1][0]) / 2;
                    const midLng = (flight.route[0][1] + flight.route[flight.route.length - 1][1]) / 2;
                    
                    return (
                      <MapContainer
                        center={[midLat, midLng]}
                        zoom={2}
                        style={{ height: "100%", width: "100%" }}
                        zoomControl={false}
                        dragging={false}
                        scrollWheelZoom={false}
                        doubleClickZoom={false}
                        attributionControl={false}
                      >
                        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                        <Polyline
                          positions={flight.route}
                          color={flight.status === 'critical' ? '#ef4444' : flight.status === 'delayed' ? '#f59e0b' : '#14b8a6'}
                          weight={3}
                          opacity={0.9}
                        />
                        <Marker
                          position={flight.route[Math.floor(flight.route.length / 2)]}
                          icon={new L.DivIcon({ 
                            className: "custom-plane", 
                            html: "✈️", 
                            iconSize: [20, 20], 
                            iconAnchor: [10, 10] 
                          })}
                        />
                      </MapContainer>
                    );
                  }
                  return (
                    <div className="flex items-center justify-center h-full text-slate-500 text-xs">
                      No route data
                    </div>
                  );
                })()
              ) : (
                <div className="flex items-center justify-center h-full text-slate-500 text-xs">
                  No flight linked
                </div>
              )}
            </div>

            <div className="mb-2">
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-2 rounded-full ${
                    risk.riskScore > 0.7
                      ? "bg-rose-500"
                      : risk.riskScore > 0.4
                      ? "bg-amber-400"
                      : "bg-green-500"
                  }`}
                  style={{ width: `${risk.riskScore * 100}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                Risk Score: {(risk.riskScore * 100).toFixed(0)}%
              </p>
            </div>

            <h3 className="text-sm font-semibold">{risk.suggestedAction}</h3>
            <p className="text-xs text-gray-400 mb-2">ROI: {risk.roi}</p>

            <div className="flex gap-2 mt-auto">
              <button
                className="flex-1 bg-emerald-600 px-2 py-1 rounded text-xs hover:bg-emerald-500"
                onClick={() => setShowModal(true)}
              >
                Apply
              </button>
              <button
                className="flex-1 bg-slate-700 px-2 py-1 rounded text-xs hover:bg-slate-600"
                onClick={() => alert(`Simulate ${risk.suggestedAction}`)}
              >
                Simulate
              </button>
              <button
                className="flex-1 bg-cyan-600 px-2 py-1 rounded text-xs hover:bg-cyan-500"
                onClick={() => setSelectedRisk(risk)}
              >
                Open
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Slide-over Detail Panel */}
      {/* {selectedRisk && (
        <aside className="fixed right-0 top-0 w-full md:w-96 h-full p-6 bg-[#112b4a] rounded-l-2xl shadow-lg flex flex-col overflow-y-auto z-40">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">
              {selectedRisk.suggestedAction}
            </h2>
            <button onClick={() => setSelectedRisk(null)}>✕</button>
          </div>

          {/* Tabs */}
      {/* <div className="flex gap-2 mb-4 text-xs font-semibold">
            <button className="px-2 py-1 rounded bg-teal-600">Timeline</button>
            <button className="px-2 py-1 rounded bg-teal-500/50">
              Explainability
            </button>
            <button className="px-2 py-1 rounded bg-teal-500/50">Action</button>
          </div>

          {/* Timeline */}
      {/* <div className="mb-4">
            <h4 className="text-sm font-semibold mb-2">Timeline</h4>
            <ul className="text-xs text-gray-400 space-y-1">
              {selectedRisk.timelineEvents.map((e, i) => (
                <li key={i}>
                  <span className="font-semibold">{e.time}</span> - {e.event}
                </li>
              ))}
            </ul>
          </div> */}

      {/* Explainability */}
      {/* <div className="mb-4">
            <h4 className="text-sm font-semibold mb-2">Explainability</h4>
            <Bar
              data={getBarData(selectedRisk.topFeatures)}
              options={{ plugins: { legend: { display: false } } }}
            />
            <p className="text-xs text-gray-400 mt-2">
              {selectedRisk.cortexNarrative}
            </p>
          </div> */}

      {/* Action Panel */}
      {/* <div className="mb-4">
            <h4 className="text-sm font-semibold mb-2">Action Panel</h4>
            <p className="text-xs text-gray-400 mb-1">
              Recommended: {selectedRisk.suggestedAction}
            </p>
            <p className="text-xs text-gray-400 mb-1">
              ROI: {selectedRisk.roi}
            </p>
            <p className="text-xs text-gray-400">
              Last Updated: {selectedRisk.lastUpdated}
            </p>
          </div>
        </aside>
      )} */}
      {/* Slide-over Detail Panel */}
      {selectedRisk && (
        <aside className="fixed right-0 top-0 w-full md:w-96 h-full p-6 bg-[#112b4a] rounded-l-2xl shadow-lg flex flex-col overflow-y-auto z-40">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">
              {selectedRisk.suggestedAction}
            </h2>
            <button
              onClick={() => setSelectedRisk(null)}
              className="text-gray-300 hover:text-white font-bold"
            >
              ✕
            </button>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-4 text-xs font-semibold">
            <button className="px-2 py-1 rounded bg-teal-600">Timeline</button>
            <button className="px-2 py-1 rounded bg-teal-500/50">
              Explainability
            </button>
            <button className="px-2 py-1 rounded bg-teal-500/50">Action</button>
          </div>

          {/* Timeline */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold mb-2">Timeline</h4>
            <ul className="text-xs text-gray-400 space-y-1">
              {selectedRisk.timelineEvents.map((e, i) => (
                <li key={i}>
                  <span className="font-semibold">{e.time}</span> - {e.event}
                </li>
              ))}
            </ul>
          </div>

          {/* Explainability */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold mb-2">Explainability</h4>
            <Bar
              data={getBarData(selectedRisk.topFeatures)}
              options={{ plugins: { legend: { display: false } } }}
            />
            <p className="text-xs text-gray-400 mt-2">
              {selectedRisk.cortexNarrative}
            </p>
          </div>

          {/* Action Panel */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold mb-2">Action Panel</h4>
            <p className="text-xs text-gray-400 mb-1">
              Recommended: {selectedRisk.suggestedAction}
            </p>
            <p className="text-xs text-gray-400 mb-1">
              ROI: {selectedRisk.roi}
            </p>
            <p className="text-xs text-gray-400">
              Last Updated: {selectedRisk.lastUpdated}
            </p>
          </div>

          {/* Sticky Footer Buttons */}
          <div className="mt-auto flex gap-3 sticky bottom-0 bg-[#112b4a] py-3">
            <button
              className="flex-1 bg-slate-700 px-3 py-2 rounded hover:bg-slate-600"
              onClick={() => setSelectedRisk(null)}
            >
              Close
            </button>
            <button
              className="flex-1 bg-emerald-600 px-3 py-2 rounded hover:bg-emerald-500"
              onClick={() => {
                alert(`Action Applied: ${selectedRisk.suggestedAction}`);
                setSelectedRisk(null);
              }}
            >
              Apply Action
            </button>
          </div>
        </aside>
      )}

      {/* Apply Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#112b4a] p-6 rounded-2xl shadow-lg w-96">
            <h3 className="text-lg font-semibold mb-4">Apply Action</h3>
            <p className="text-gray-300 mb-4">
              Confirm applying the recommended action.
            </p>
            <div className="flex justify-end gap-2">
              <button
                className="px-3 py-1 bg-gray-600 rounded hover:bg-gray-500"
                onClick={() => setShowModal(false)}
              >
                Cancel
              </button>
              <button
                className="px-3 py-1 bg-emerald-600 rounded hover:bg-emerald-500"
                onClick={() => {
                  alert("Action Applied!");
                  setShowModal(false);
                }}
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Top Risky Table */}
      <div className="overflow-x-auto mt-10">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-teal-300 font-semibold">
            Top Risky Flights / Machines
          </h3>
          <div className="flex gap-3">
            <select
              className="px-3 py-1.5 glass-card rounded-lg text-white text-xs border border-gray-700 shadow-md focus:ring-2 focus:ring-teal-400"
              value={tableFilters.type}
              onChange={(e) => setTableFilters({...tableFilters, type: e.target.value})}
            >
              <option value="all">All Types</option>
              <option value="Flight">Flights Only</option>
              <option value="Machine">Machines Only</option>
            </select>
            <select
              className="px-3 py-1.5 glass-card rounded-lg text-white text-xs border border-gray-700 shadow-md focus:ring-2 focus:ring-teal-400"
              value={tableFilters.status}
              onChange={(e) => setTableFilters({...tableFilters, status: e.target.value})}
            >
              <option value="all">All Risk Levels</option>
              <option value="High Risk">High Risk</option>
              <option value="Medium Risk">Medium Risk</option>
              <option value="Low Risk">Low Risk</option>
            </select>
            <select
              className="px-3 py-1.5 glass-card rounded-lg text-white text-xs border border-gray-700 shadow-md focus:ring-2 focus:ring-teal-400"
              value={tableFilters.sortBy}
              onChange={(e) => setTableFilters({...tableFilters, sortBy: e.target.value})}
            >
              <option value="desc">Score: High to Low</option>
              <option value="asc">Score: Low to High</option>
            </select>
          </div>
        </div>
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="glass-card">
              <th className="px-4 py-2">Identifier</th>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Score</th>
              <th className="px-4 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {topRiskyData
              .filter(row => tableFilters.type === "all" || row.type === tableFilters.type)
              .filter(row => tableFilters.status === "all" || row.status === tableFilters.status)
              .sort((a, b) => tableFilters.sortBy === "desc" ? b.score - a.score : a.score - b.score)
              .map((row, i) => (
              <tr
                key={row.id}
                className={`${
                  i % 2 === 0 ? "bg-[#112b4a]" : "glass-card"
                } hover:bg-teal-700/30 transition cursor-pointer`}
              >
                <td className="px-4 py-2">{row.identifier}</td>
                <td className="px-4 py-2">{row.type}</td>
                <td className="px-4 py-2 font-semibold">{row.score}</td>
                <td className="px-4 py-2">
                  <span
                    className={`px-2 py-1 rounded text-xs font-semibold ${
                      row.status === "High Risk"
                        ? "bg-red-500 text-white"
                        : row.status === "Medium Risk"
                        ? "bg-amber-400 text-black"
                        : "bg-green-500 text-white"
                    }`}
                  >
                    {row.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
