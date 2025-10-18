import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

import { Line, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

import { RISKS, RISK_SEVERITY, FLIGHTS, FINANCIAL_DATA, PERFORMANCE_HISTORY, FACILITIES } from "../data/mockData";
import { MapContainer, TileLayer, Polyline, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useNavigate } from "react-router-dom";
import PanicButton from "../components/PanicButton";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// ---------- Helpers ----------
function formatCurrency(n) {
  if (n == null) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

// Calculate KPIs from real data
const calculateKPIs = () => {
  const highRisks = RISKS.filter(r => r.severity === RISK_SEVERITY.HIGH || r.severity === RISK_SEVERITY.CRITICAL).length;
  const mediumRisks = RISKS.filter(r => r.severity === RISK_SEVERITY.MEDIUM).length;
  const lowRisks = RISKS.filter(r => r.severity === RISK_SEVERITY.LOW).length;
  
  const avgETADrift = FLIGHTS.reduce((sum, f) => sum + Math.abs(f.etaDrift), 0) / FLIGHTS.length;
  
  const recentOTIF = PERFORMANCE_HISTORY.last30Days.otif.slice(-7);
  const avgOTIF = recentOTIF.reduce((sum, val) => sum + val, 0) / recentOTIF.length;

  return {
    otif: Math.round(avgOTIF * 10) / 10,
    activeRisks: { high: highRisks, medium: mediumRisks, low: lowRisks },
    moneySavedYTD: FINANCIAL_DATA.ytdSavingsFromAI,
    avgETADrift: Math.round(avgETADrift * 10) / 10,
  };
};

const MOCK_KPIS = calculateKPIs();

// Generate recommendations from actual risks
const MOCK_RECOMMENDATIONS = RISKS.filter(r => r.priority === "urgent" || r.severity === RISK_SEVERITY.HIGH)
  .slice(0, 3)
  .map(risk => ({
    id: risk.id,
    title: risk.suggestedAction,
    roi: risk.roi,
    brief: risk.description.substring(0, 60) + "...",
    flightId: risk.flightId,
    machineId: risk.machineId,
  }));

const MOCK_ACTIVITIES = [
  `AI recommended expedite for ${FLIGHTS[0].flightNumber} — ROI ${RISKS[0].roi}`,
  `Risk RISK-10848 escalated to Ops Team Beta — urgent action`,
  `Machine M-3892-C health dropped to 78% — alert triggered`,
  `Model v2.1 deployed — improved prediction accuracy by 6.3%`,
  `Simulated spare routing — estimated OTIF improvement +2.1%`,
  `Flight ${FLIGHTS[4].flightNumber} expedited — saved $70.3K downtime`,
];

// ---------- Chart Data ----------
const costTrendData = {
  labels: ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
  datasets: [
    {
      label: "Monthly Costs ($K)",
      data: PERFORMANCE_HISTORY.last12Months.costs.map(c => c / 1000),
      borderColor: "#00f6ff",
      backgroundColor: "rgba(0,246,255,0.2)",
      tension: 0.4,
      fill: true,
    },
  ],
};

const delaysData = {
  labels: Object.keys(FACILITIES).slice(0, 5).map(key => FACILITIES[key].name.split(' ')[0]),
  datasets: [
    {
      label: "Delays Avoided (count)",
      data: [87, 92, 73, 65, 81],
      backgroundColor: "rgba(16, 185, 129, 0.6)", // emerald glow
    },
  ],
};

// ---------- Component ----------
export default function ExecutiveAIDashboard() {
  const navigate = useNavigate();
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recs, setRecs] = useState(MOCK_RECOMMENDATIONS);
  const [mapLoading, setMapLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => {
      setKpis(MOCK_KPIS);
      setLoading(false);
    }, 700);
    
    // Simulate map loading
    const mapTimer = setTimeout(() => {
      setMapLoading(false);
    }, 1000);
    
    return () => {
      clearTimeout(t);
      clearTimeout(mapTimer);
    };
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      {/* HEADER */}
      <header className="flex flex-wrap items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-cyan-400 text-transparent bg-clip-text">
            Executive AI Command Center
          </h1>
          <p className="text-sm text-slate-400">
            Real-time metrics · AI recommendations · Digital Twin snapshot
          </p>
        </div>
        <div className="flex flex-wrap gap-3 items-center">
          <PanicButton variant="default" />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 rounded-xl glass-card glass-card-hover border border-purple-500/30 text-sm font-semibold text-white flex items-center gap-2 shadow-lg hover:border-purple-400/50 transition-all"
            onClick={() => navigate('/cinematic-twin')}
          >
            <span>🎬</span>
            <span>Cinematic Twin</span>
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 rounded-xl glass-card glass-card-hover border border-teal-500/30 text-sm font-semibold text-white shadow-lg hover:border-teal-400/50 transition-all"
            onClick={() => navigate('/map')}
          >
            Launch Full Twin →
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-4 py-2 rounded-xl glass-card glass-card-hover border border-blue-500/30 text-sm font-semibold text-white flex items-center gap-2 shadow-lg hover:border-blue-400/50 transition-all"
            onClick={() => navigate('/executive-brief')}
          >
            <span>📊</span>
            <span>Executive Brief</span>
          </motion.button>
        </div>
      </header>

      {/* KPI CARDS */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <motion.div
          whileHover={{ scale: 1.03 }}
          className="p-6 rounded-2xl glass-card glass-card-hover glass-card-glow flex flex-col"
        >
          <p className="text-sm text-gray-400">OTIF %</p>
          <h2 className="text-3xl font-bold text-emerald-400">
            {loading ? "—" : `${kpis?.otif}%`}
          </h2>
          <span className="text-xs text-slate-400 mt-1">On-Time & In-Full</span>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.03 }}
          className={`p-6 rounded-2xl glass-card glass-card-hover glass-card-glow flex flex-col relative ${
            kpis?.activeRisks?.high > 0 ? 'pulse-glow-critical' : ''
          }`}
        >
          {kpis?.activeRisks?.high > 0 && (
            <div className="absolute top-2 right-2 w-3 h-3 bg-red-500 rounded-full pulse-critical"></div>
          )}
          <p className="text-sm text-gray-400">Active Risks</p>
          <h2 className={`text-3xl font-bold text-rose-400 ${kpis?.activeRisks?.high > 0 ? 'heartbeat' : ''}`}>
            {loading
              ? "—"
              : Object.values(kpis?.activeRisks ?? {}).reduce(
                  (a, b) => a + b,
                  0
                )}
          </h2>
          <span className="text-xs text-slate-400 mt-1">
            H {kpis?.activeRisks?.high ?? "—"} · M{" "}
            {kpis?.activeRisks?.medium ?? "—"} · L{" "}
            {kpis?.activeRisks?.low ?? "—"}
          </span>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.03 }}
          className="p-6 rounded-2xl glass-card glass-card-hover glass-card-glow flex flex-col"
        >
          <p className="text-sm text-gray-400">Money Saved (YTD)</p>
          <h2 className="text-3xl font-bold text-teal-400">
            {loading ? "—" : formatCurrency(kpis?.moneySavedYTD)}
          </h2>
          <span className="text-xs text-slate-400 mt-1">Rolling impact</span>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.03 }}
          className="p-6 rounded-2xl glass-card glass-card-hover glass-card-glow flex flex-col"
        >
          <p className="text-sm text-gray-400">Avg ETA Drift (min)</p>
          <h2 className="text-3xl font-bold text-cyan-400">
            {loading ? "—" : `${kpis?.avgETADrift ?? "—"}m`}
          </h2>
          <span className="text-xs text-slate-400 mt-1">
            Average delay vs ETA
          </span>
        </motion.div>
      </section>

      {/* MAIN GRID */}
      {/* MAIN GRID */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* LEFT: Mini Digital Twin */}
        <div className="lg:col-span-2 glass-card glass-card-glow rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold">Mini Digital Twin</h3>
            <div className="text-xs text-slate-400">
              Snapshot · Hover to preview
            </div>
          </div>

          {/* Embedded Leaflet mini-map showing active flight routes */}
          <div className="h-[500px] rounded overflow-hidden relative">
            {mapLoading && (
              <div className="absolute inset-0 bg-black/60 z-10 flex items-center justify-center">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-teal-400 border-t-transparent"></div>
                  <p className="mt-3 text-sm text-slate-400">Loading Digital Twin...</p>
                </div>
              </div>
            )}
            <MapContainer center={[20, 0]} zoom={2} style={{ height: "100%", width: "100%" }} className="rounded">
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
              {FLIGHTS.map((f) => (
                f.route && f.route.length > 1 ? (
                  <React.Fragment key={f.id}>
                    <Polyline positions={f.route} color={f.status === 'critical' ? '#ef4444' : f.status === 'delayed' ? '#f59e0b' : '#14b8a6'} weight={2} opacity={0.6} />
                    <Marker position={f.route[Math.floor(f.route.length / 2)]} icon={new L.DivIcon({ className: "custom-plane", html: "✈️", iconSize: [24, 24], iconAnchor: [12, 12] })}>
                      <Popup>
                        <div className="text-gray-900 text-xs">
                          <strong>{f.flightNumber}</strong><br />
                          {f.from} → {f.to}<br />
                          Status: {f.status.replace('_', ' ')}<br />
                          ETA Drift: {f.etaDrift > 0 ? '+' : ''}{f.etaDrift} min
                        </div>
                      </Popup>
                    </Marker>
                  </React.Fragment>
                ) : null
              ))}
            </MapContainer>
          </div>

          <div className="mt-4 flex items-center gap-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-500 focus:outline focus:outline-2 focus:outline-emerald-400 transition"
              onClick={() => navigate('/map')}
            >
              Open Full Twin
            </motion.button>
            <div className="ml-auto text-xs text-slate-400">
              {FLIGHTS.length} Active Flights · {FACILITIES && Object.keys(FACILITIES).length} Facilities · Live
            </div>
          </div>
        </div>

        {/* RIGHT: AI Insights & Recent Activity */}
        <aside className="lg:col-span-1 space-y-6">
          {/* AI Insights */}
          <motion.div
            className="p-6 rounded-2xl glass-card glass-card-glow flex flex-col"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <h3 className="text-cyan-400 font-semibold mb-3">
              AI Insights & Recommendations
            </h3>

            <ul className="mt-3 space-y-2">
              {recs.map((r) => (
                <li
                  key={r.id}
                  className="flex items-center justify-between p-2 bg-slate-800 rounded"
                >
                  <div>
                    <div className="text-sm font-medium">{r.title}</div>
                    <div className="text-xs text-slate-400">{r.brief}</div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <div className="text-xs text-slate-400">{r.roi}</div>
                    <div className="flex gap-2">
                      <button
                        className="px-2 py-1 rounded text-xs bg-emerald-600 hover:bg-emerald-500"
                        onClick={() =>
                          window.alert(`Apply action (demo): ${r.title}`)
                        }
                      >
                        Apply
                      </button>
                      <button
                        className="px-2 py-1 rounded text-xs bg-slate-700 hover:bg-slate-600"
                        onClick={() =>
                          window.alert(`Simulate action (demo): ${r.title}`)
                        }
                      >
                        Simulate
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>

            <button className="mt-auto px-4 py-2 rounded-lg bg-gradient-to-r from-teal-400 to-cyan-400 text-[#0a192f] font-semibold hover:opacity-90 transition">
              View Full Report →
            </button>
          </motion.div>

          {/* Recent Activity */}
          <motion.div
            className="p-6 rounded-2xl glass-card glass-card-glow"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <h4 className="text-emerald-400 font-semibold mb-2">
              Recent Activity
            </h4>
            <ul className="text-sm text-slate-300 space-y-2">
              {MOCK_ACTIVITIES.map((a, i) => (
                <li
                  key={i}
                  className="p-2 bg-slate-800/60 rounded hover:bg-slate-700/60 transition"
                >
                  {a}
                </li>
              ))}
            </ul>
          </motion.div>
        </aside>
      </section>

      {/* CHARTS ROW: Side by side */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        {/* Cost Trend */}
        <motion.div
          className="p-6 rounded-2xl glass-card glass-card-glow"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h3 className="text-teal-400 font-semibold mb-2">Cost Trends</h3>
          <p className="text-gray-400 text-sm mb-4">
            Last 12 months · YTD savings: {formatCurrency(FINANCIAL_DATA.ytdSavingsFromAI)}
          </p>
          <Line
            data={costTrendData}
            options={{
              responsive: true,
              plugins: { legend: { display: false } },
            }}
          />
        </motion.div>

        {/* Delays Avoided */}
        <motion.div
          className="p-6 rounded-2xl glass-card glass-card-glow"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h4 className="text-emerald-400 font-semibold mb-2">
            Delays Avoided
          </h4>
          <p className="text-gray-400 mb-4">Last Quarter +12%</p>
          <Bar
            data={delaysData}
            options={{
              responsive: true,
              plugins: { legend: { display: false } },
            }}
          />
        </motion.div>
      </section>

      {/* FOOTER */}
      <footer className="mt-10 text-xs text-slate-500 text-center">
        Powered by Snowflake · Aeroline Demo · Hackathon 2025
      </footer>
    </main>
  );
}
