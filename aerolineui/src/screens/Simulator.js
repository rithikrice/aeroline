import { useState, useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { TrendingUp, DollarSign, Clock, AlertTriangle, CheckCircle, Info } from "lucide-react";

import { FINANCIAL_DATA, FACILITIES } from "../data/mockData";

export default function WhatIfSimulator() {
  // Initialize with realistic values from our data
  const baseRevenue = FINANCIAL_DATA.monthlyTargets.revenue;
  const avgDowntimeCost = FINANCIAL_DATA.avgDowntimeCostPerHour;
  
  const [selectedFacility, setSelectedFacility] = useState(Object.keys(FACILITIES)[0]);
  const [downtimeHours, setDowntimeHours] = useState(8);
  const [expediteFee, setExpediteFee] = useState(FINANCIAL_DATA.avgExpediteFee);
  const [penaltyCost, setPenaltyCost] = useState(FINANCIAL_DATA.avgDelayPenalty);

  const downtime = downtimeHours * avgDowntimeCost;
  const expedite = expediteFee;
  const penalty = penaltyCost;

  const roi = baseRevenue - downtime - expedite - penalty;
  const baseline = baseRevenue - (4 * avgDowntimeCost) - FINANCIAL_DATA.avgExpediteFee - FINANCIAL_DATA.avgDelayPenalty;
  const roiChange = ((roi - baseline) / baseline) * 100;

  // ROI Curve: Shows projected ROI over time based on current parameters
  const roiData = useMemo(() => {
    const baseROI = baseRevenue / 1000;
    const downtimeImpact = (downtime / 1000) / 30; // spread over days
    const expediteImpact = (expedite / 1000) / 30;
    const penaltyImpact = (penalty / 1000) / 30;
    
    return Array.from({ length: 30 }, (_, i) => ({
      day: i + 1,
      value: Math.max(0, baseROI - (downtimeImpact * (i + 1)) - (expediteImpact * Math.sin(i / 3)) - (penaltyImpact * (i % 7 === 0 ? 1.5 : 0.5))),
    }));
  }, [downtime, expedite, penalty, baseRevenue]);

  // Trade-off Curve: Cost vs Speed optimisation
  const tradeoffData = useMemo(() => {
    return Array.from({ length: 20 }, (_, i) => {
      const speedFactor = i / 20; // 0 to 1
      const costMultiplier = expedite / FINANCIAL_DATA.avgExpediteFee;
      const downtimeMultiplier = downtimeHours / 4;
      
      return {
        cost: Math.round((i * costMultiplier * 5)),
        speed: Math.round(100 - (50 * Math.pow(1 - speedFactor, 2)) * downtimeMultiplier),
        label: `${Math.round(speedFactor * 100)}%`,
      };
    });
  }, [downtime, expedite, penalty, downtimeHours]);

  const facilityData = FACILITIES[selectedFacility];

  return (
    <div className="min-h-screen bg-slate-950 text-white p-10 font-sans">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-4xl font-bold text-teal-400 mb-2">
              What-If Simulator
      </h1>
            <p className="text-gray-400">
              Adjust parameters to simulate different scenarios and optimise decision-making
            </p>
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-2">Select Facility</label>
            <select
              value={selectedFacility}
              onChange={(e) => setSelectedFacility(e.target.value)}
              className="px-4 py-2 glass-card rounded-lg text-white border border-teal-400 focus:ring-2 focus:ring-teal-400"
            >
              {Object.entries(FACILITIES).map(([key, facility]) => (
                <option key={key} value={key}>
                  {facility.name} - {facility.city}
                </option>
              ))}
            </select>
          </div>
        </div>
        {facilityData && (
          <div className="glass-card rounded-lg p-4 mt-4 flex gap-6 text-sm">
            <div>
              <span className="text-gray-400">Location:</span>{" "}
              <span className="text-white font-semibold">{facilityData.city}, {facilityData.country}</span>
            </div>
            <div>
              <span className="text-gray-400">Capacity:</span>{" "}
              <span className="text-white font-semibold">{facilityData.capacity.toLocaleString()} units/day</span>
            </div>
            <div>
              <span className="text-gray-400">Facility ID:</span>{" "}
              <span className="text-teal-400 font-mono text-xs">{selectedFacility}</span>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-8">
        {/* Left Side */}
        <div className="col-span-2 space-y-8">
          {/* Current Scenario Summary */}
          <div className="grid grid-cols-3 gap-4">
            <div className="glass-card rounded-xl p-4 border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-orange-400" />
                <span className="text-xs text-gray-400">Downtime</span>
              </div>
              <p className="text-2xl font-bold text-orange-400">{downtimeHours}h</p>
              <p className="text-xs text-gray-500 mt-1">${downtime.toLocaleString()} cost</p>
            </div>
            <div className="glass-card rounded-xl p-4 border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-blue-400" />
                <span className="text-xs text-gray-400">Expedite</span>
              </div>
              <p className="text-2xl font-bold text-blue-400">${expedite.toLocaleString()}</p>
              <p className="text-xs text-gray-500 mt-1">Per shipment</p>
            </div>
            <div className="glass-card rounded-xl p-4 border border-white/10">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                <span className="text-xs text-gray-400">Penalty</span>
              </div>
              <p className="text-2xl font-bold text-red-400">${penalty.toLocaleString()}</p>
              <p className="text-xs text-gray-500 mt-1">Per incident</p>
            </div>
          </div>

          {/* Sliders */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 shadow-lg">
            <h3 className="text-lg font-semibold text-teal-300 mb-4">Adjust Parameters</h3>
            <SliderWithLabel
              label="Downtime Duration (hours)"
              value={downtimeHours}
              setValue={setDowntimeHours}
              min={0}
              max={24}
              unit="hours"
              description={`Total cost impact: $${downtime.toLocaleString()}`}
            />
            <SliderWithLabel
              label="Expedite Fee"
              value={expediteFee}
              setValue={setExpediteFee}
              min={1000}
              max={30000}
              unit="$"
              description="Cost to fast-track critical shipment"
            />
            <SliderWithLabel
              label="Delay Penalty"
              value={penaltyCost}
              setValue={setPenaltyCost}
              min={5000}
              max={50000}
              unit="$"
              description="Contract penalty for missed deadlines"
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-2 gap-6">
            {/* ROI Curve */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 shadow-lg fade-in">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-teal-300">
                  📈 30-Day ROI Projection ($K)
              </h2>
                <div className="text-right">
                  <p className="text-xs text-gray-400">30-Day Delta</p>
                  <p className={`text-lg font-bold ${roiChange > 0 ? 'text-green-400' : roiChange < 0 ? 'text-red-400' : 'text-gray-400'}`}>
                    {roiChange > 0 ? '+' : ''}{roiChange.toFixed(1)}%
                  </p>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={roiData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f3558" />
                  <XAxis dataKey="day" stroke="#aaa" label={{ value: "Days", position: "insideBottom", offset: -5 }} />
                  <YAxis stroke="#aaa" label={{ value: "$K", angle: -90, position: "insideLeft" }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f223f",
                      borderRadius: "10px",
                      border: "1px solid #00f5d4",
                    }}
                    formatter={(value) => [`$${value.toFixed(1)}K`, "ROI"]}
                  />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#00f5d4"
                    strokeWidth={3}
                    dot={{ fill: "#00f5d4", r: 4 }}
                    activeDot={{ r: 6, fill: '#00f5d4', stroke: '#0a192f', strokeWidth: 2 }}
                    isAnimationActive={true}
                    animationDuration={800}
                    animationEasing="ease-in-out"
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-3 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: '#00f5d4' }}></div>
                  <span className="text-gray-400">Current Scenario</span>
                </div>
                <div className="text-gray-500">
                  End Value: <span className="text-white font-semibold">${roiData[roiData.length - 1]?.value.toFixed(1)}K</span>
                </div>
              </div>
            </div>

            {/* Trade-off Curve */}
            <div className="glass-card rounded-2xl p-6 border border-white/10 shadow-lg fade-in">
              <h2 className="text-lg font-semibold text-teal-300 mb-4">
                ⚖️ Cost vs. Speed Trade-off
              </h2>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={tradeoffData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f3558" />
                  <XAxis dataKey="cost" stroke="#aaa" label={{ value: "Cost ($)", position: "insideBottom", offset: -5 }} />
                  <YAxis stroke="#aaa" label={{ value: "Speed (%)", angle: -90, position: "insideLeft" }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f223f",
                      borderRadius: "10px",
                      border: "1px solid #f59e0b",
                    }}
                    formatter={(value, name) => {
                      if (name === "speed") return [`${value}%`, "Delivery Speed"];
                      return [`$${value}`, "Cost"];
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="speed"
                    stroke="#f59e0b"
                    strokeWidth={3}
                    dot={{ fill: "#f59e0b", r: 4 }}
                    activeDot={{ r: 6, fill: '#f59e0b', stroke: '#0a192f', strokeWidth: 2 }}
                    isAnimationActive={true}
                    animationDuration={800}
                    animationEasing="ease-in-out"
                  />
                </LineChart>
              </ResponsiveContainer>
              <div className="mt-3 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                  <span className="text-gray-400">Optimisation Curve</span>
                </div>
                <p className="text-gray-500">
                  Higher costs enable faster delivery with diminishing returns
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Analysis Sidebar */}
        <div className="space-y-6">
          {/* Current Scenario */}
        <div className="glass-card rounded-2xl p-6 border border-white/10 shadow-lg">
          <h2 className="text-lg font-semibold text-teal-300 mb-4">
              <DollarSign className="inline w-5 h-5 mr-2" />
              Financial Impact
          </h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-400 mb-1">Projected ROI</p>
                <p className="text-3xl font-bold text-teal-400">
              ${roi.toLocaleString()}
                </p>
                <p className={`text-sm mt-1 ${roiChange >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {roiChange >= 0 ? "↑" : "↓"} {Math.abs(roiChange).toFixed(1)}% vs baseline
                </p>
              </div>
              
              <div className="pt-4 border-t border-gray-700">
                <p className="text-xs text-gray-500 mb-3">Cost Breakdown:</p>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Base Revenue:</span>
                    <span className="text-white font-semibold">${baseRevenue.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Downtime Loss:</span>
                    <span className="text-red-400">-${downtime.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Expedite Cost:</span>
                    <span className="text-orange-400">-${expedite.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Penalties:</span>
                    <span className="text-red-400">-${penalty.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Insights */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 shadow-lg">
            <h2 className="text-lg font-semibold text-teal-300 mb-4">
              🤖 AI Insights
            </h2>
            <div className="space-y-3 text-sm">
              {downtimeHours > 12 ? (
                <div className="bg-red-900/20 border border-red-700/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-300 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-red-300 font-semibold mb-1">High Downtime Risk</p>
                      <p className="text-gray-300 text-xs">
                        {downtimeHours} hours of downtime at {facilityData.name} significantly impacts profitability. 
                        Consider expediting critical parts or implementing preventive maintenance.
                      </p>
                      <p className="text-red-200 text-xs mt-2">
                        💡 Recommendation: Reduce downtime to &lt;10 hours for {Math.round(((10 * avgDowntimeCost - downtime) / 1000))} savings
                      </p>
                    </div>
                  </div>
                </div>
              ) : downtimeHours < 4 ? (
                <div className="bg-green-900/20 border border-green-700/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-300 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-green-300 font-semibold mb-1">Excellent Uptime</p>
                      <p className="text-gray-300 text-xs">
                        Low downtime of {downtimeHours} hours indicates strong operational efficiency. 
                        This is {Math.round((1 - downtimeHours / 8) * 100)}% better than baseline.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-blue-900/20 border border-blue-700/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <Info className="w-4 h-4 text-blue-300 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-blue-300 font-semibold mb-1">Normal Operations</p>
                      <p className="text-gray-300 text-xs">
                        Current downtime of {downtimeHours} hours is within acceptable range for {facilityData.name}.
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {expedite > 20000 && (
                <div className="bg-yellow-900/20 border border-yellow-700/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <DollarSign className="w-4 h-4 text-yellow-300 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-yellow-300 font-semibold mb-1">High Expedite Costs</p>
                      <p className="text-gray-300 text-xs">
                        Expedite fee of ${expedite.toLocaleString()} is {Math.round(expedite / FINANCIAL_DATA.avgExpediteFee * 100)}% 
                        above average. Evaluate if ROI justifies premium cost.
                      </p>
                      <p className="text-yellow-200 text-xs mt-2">
                        💡 Standard expedite: ${FINANCIAL_DATA.avgExpediteFee.toLocaleString()} | Current: ${expedite.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {roiChange > 5 && (
                <div className="bg-green-900/20 border border-green-700/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <TrendingUp className="w-4 h-4 text-green-300 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-green-300 font-semibold mb-1">Optimal Scenario</p>
                      <p className="text-gray-300 text-xs">
                        Current parameters show {roiChange.toFixed(1)}% improvement over baseline at {facilityData.name}. 
                        This configuration balances cost and risk effectively.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {roiChange < -10 && (
                <div className="bg-red-900/20 border border-red-700/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-300 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-red-300 font-semibold mb-1">Below Target</p>
                      <p className="text-gray-300 text-xs">
                        ROI is {Math.abs(roiChange).toFixed(1)}% below baseline at {facilityData.name}. 
                        Adjust parameters to improve profitability.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {roiChange >= -10 && roiChange <= 5 && downtimeHours >= 4 && downtimeHours <= 12 && expedite <= 20000 && (
                <div className="bg-gray-800/40 border border-gray-700/30 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <Info className="w-4 h-4 text-gray-300 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-gray-300 font-semibold mb-1">Baseline Performance</p>
                      <p className="text-gray-400 text-xs">
                        All parameters within normal operational ranges for {facilityData.name}. 
                        Try adjusting sliders to explore optimisation opportunities.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="glass-card rounded-2xl p-6 border border-white/10 shadow-lg">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">Quick Scenarios</h3>
            <div className="space-y-3">
              <button 
                onClick={() => {
                  setDowntimeHours(2);
                  setExpediteFee(FINANCIAL_DATA.avgExpediteFee * 0.8);
                  setPenaltyCost(FINANCIAL_DATA.avgDelayPenalty * 0.5);
                }}
                className="w-full text-left px-3 py-3 rounded-lg bg-green-900/20 hover:bg-green-900/30 border border-green-700/30 transition-all"
              >
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-300 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-green-300 font-semibold text-xs">Best Case Scenario</p>
                    <p className="text-gray-400 text-xs mt-1">
                      Minimal disruption · Proactive maintenance · Optimal inventory
                    </p>
                    <div className="flex gap-3 mt-2 text-xs text-gray-500">
                      <span>Downtime: 2h</span>
                      <span>Expedite: ~${Math.round(FINANCIAL_DATA.avgExpediteFee * 0.8).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </button>
              <button 
                onClick={() => {
                  setDowntimeHours(8);
                  setExpediteFee(FINANCIAL_DATA.avgExpediteFee);
                  setPenaltyCost(FINANCIAL_DATA.avgDelayPenalty);
                }}
                className="w-full text-left px-3 py-3 rounded-lg bg-yellow-900/20 hover:bg-yellow-900/30 border border-yellow-700/30 transition-all"
              >
                <div className="flex items-start gap-2">
                  <Info className="w-4 h-4 text-yellow-300 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-yellow-300 font-semibold text-xs">Typical Scenario</p>
                    <p className="text-gray-400 text-xs mt-1">
                      Average operational conditions · Standard risk factors
                    </p>
                    <div className="flex gap-3 mt-2 text-xs text-gray-500">
                      <span>Downtime: 8h</span>
                      <span>Expedite: ${FINANCIAL_DATA.avgExpediteFee.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </button>
              <button 
                onClick={() => {
                  setDowntimeHours(18);
                  setExpediteFee(FINANCIAL_DATA.avgExpediteFee * 2.5);
                  setPenaltyCost(FINANCIAL_DATA.avgDelayPenalty * 2.5);
                }}
                className="w-full text-left px-3 py-3 rounded-lg bg-red-900/20 hover:bg-red-900/30 border border-red-700/30 transition-all"
              >
                <div className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-300 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-red-300 font-semibold text-xs">Worst Case Scenario</p>
                    <p className="text-gray-400 text-xs mt-1">
                      Multiple failures · Supply chain disruption · Critical delays
                    </p>
                    <div className="flex gap-3 mt-2 text-xs text-gray-500">
                      <span>Downtime: 18h</span>
                      <span>Expedite: ~${Math.round(FINANCIAL_DATA.avgExpediteFee * 2.5).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function SliderWithLabel({ label, value, setValue, min, max, unit, description }) {
  return (
    <div className="mb-6">
      <div className="flex justify-between mb-2">
        <span className="text-gray-300 font-medium">{label}</span>
        <span className="text-teal-400 font-semibold">
          {unit === "$" ? "$" : ""}{value.toLocaleString()}{unit !== "$" ? ` ${unit}` : ""}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => setValue(Number(e.target.value))}
        className="w-full accent-teal-400"
        step={unit === "hours" ? 0.5 : 100}
      />
      {description && (
        <p className="text-xs text-gray-500 mt-1">{description}</p>
      )}
    </div>
  );
}
