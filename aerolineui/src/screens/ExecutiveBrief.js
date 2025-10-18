import React, { useRef, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Download, ArrowLeft, Loader2 } from "lucide-react";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import {
  RISKS,
  RISK_SEVERITY,
  FLIGHTS,
  MACHINES,
  FINANCIAL_DATA,
  PERFORMANCE_HISTORY,
  FACILITIES,
  AI_ACTIONS
} from "../data/mockData";

export default function ExecutiveBrief() {
  const navigate = useNavigate();
  const briefRef = useRef();
  const [isExporting, setIsExporting] = useState(false);

  // Calculate executive metrics
  const calculateMetrics = () => {
    const highRisks = RISKS.filter(r => r.severity === RISK_SEVERITY.HIGH || r.severity === RISK_SEVERITY.CRITICAL).length;
    const mediumRisks = RISKS.filter(r => r.severity === RISK_SEVERITY.MEDIUM).length;
    const lowRisks = RISKS.filter(r => r.severity === RISK_SEVERITY.LOW).length;
    
    const avgETADrift = FLIGHTS.reduce((sum, f) => sum + Math.abs(f.etaDrift), 0) / FLIGHTS.length;
    const criticalFlights = FLIGHTS.filter(f => f.status === 'critical').length;
    
    const recentOTIF = PERFORMANCE_HISTORY.last30Days.otif.slice(-7);
    const avgOTIF = recentOTIF.reduce((sum, val) => sum + val, 0) / recentOTIF.length;
    
    const avgMachineHealth = MACHINES.reduce((sum, m) => sum + m.health, 0) / MACHINES.length;
    const criticalMachines = MACHINES.filter(m => m.health < 70).length;

    return {
      otif: Math.round(avgOTIF * 10) / 10,
      totalRisks: highRisks + mediumRisks + lowRisks,
      highRisks,
      mediumRisks,
      lowRisks,
      criticalFlights,
      avgETADrift: Math.round(avgETADrift * 10) / 10,
      ytdSavings: FINANCIAL_DATA.ytdSavingsFromAI,
      avgMachineHealth: Math.round(avgMachineHealth),
      criticalMachines,
      totalFacilities: Object.keys(FACILITIES).length,
      totalFlights: FLIGHTS.length
    };
  };

  const metrics = calculateMetrics();

  // Get top risks
  const topRisks = RISKS
    .filter(r => r.severity === RISK_SEVERITY.HIGH || r.severity === RISK_SEVERITY.CRITICAL)
    .slice(0, 5);

  // Get recommended actions
  const recommendedActions = AI_ACTIONS.slice(0, 4);

  const exportToPDF = async () => {
    setIsExporting(true);
    try {
      const element = briefRef.current;
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#020617'
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      const imgWidth = 210;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      let heightLeft = imgHeight;
      let position = 0;

      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= 297;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= 297;
      }

      const date = new Date().toISOString().split('T')[0];
      pdf.save(`AeroLine_Executive_Brief_${date}.pdf`);
    } catch (error) {
      console.error('PDF export failed:', error);
      alert('Failed to export PDF. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      {/* Header Controls */}
      <div className="max-w-5xl mx-auto mb-6 flex justify-between items-center">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate(-1)}
          className="glass-button px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={exportToPDF}
          disabled={isExporting}
          className="px-6 py-3 rounded-lg bg-gradient-to-r from-emerald-600 to-cyan-500 flex items-center gap-2 font-semibold disabled:opacity-50"
        >
          {isExporting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Exporting...</span>
            </>
          ) : (
            <>
              <Download className="w-5 h-5" />
              <span>Export to PDF</span>
            </>
          )}
        </motion.button>
      </div>

      {/* Brief Document */}
      <div
        ref={briefRef}
        className="max-w-5xl mx-auto bg-slate-900 p-12 rounded-2xl shadow-2xl"
        style={{ minHeight: '297mm' }}
      >
        {/* Cover */}
        <div className="text-center mb-12 pb-12 border-b border-slate-700">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 text-transparent bg-clip-text mb-4">
            Executive Brief
          </h1>
          <h2 className="text-2xl text-gray-300 mb-6">
            Supply Chain Operations & Risk Analysis
          </h2>
          <div className="flex justify-center items-center gap-4 text-sm text-gray-400">
            <span>AeroLine Operations</span>
            <span>•</span>
            <span>{new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
            <span>•</span>
            <span>Confidential</span>
          </div>
          <div className="mt-8 text-xs text-gray-500">
            Powered by Snowflake Cortex AI
          </div>
        </div>

        {/* Executive Summary */}
        <section className="mb-12">
          <h3 className="text-2xl font-bold text-teal-300 mb-6">Executive Summary</h3>
          <div className="space-y-4 text-gray-300 leading-relaxed">
            <p>
              This report provides a comprehensive overview of AeroLine's real-time supply chain operations, 
              AI-driven risk assessment, and prescriptive recommendations to optimise On-Time-In-Full (OTIF) 
              performance and maximize ROI.
            </p>
            <p>
              Our AI-powered digital twin monitors <strong className="text-white">{metrics.totalFlights} active flights</strong> across 
              <strong className="text-white"> {metrics.totalFacilities} global facilities</strong>, analyzing {metrics.totalRisks} identified 
              risks and providing actionable insights to prevent disruptions before they impact operations.
            </p>
          </div>
        </section>

        {/* Key Performance Indicators */}
        <section className="mb-12">
          <h3 className="text-2xl font-bold text-teal-300 mb-6">Key Performance Indicators</h3>
          <div className="grid grid-cols-2 gap-6">
            <div className="glass-card p-6 rounded-xl">
              <div className="text-sm text-gray-400 mb-2">OTIF Performance</div>
              <div className="text-4xl font-bold text-emerald-400">{metrics.otif}%</div>
              <div className="text-xs text-gray-500 mt-2">On-Time & In-Full Delivery</div>
            </div>
            <div className="glass-card p-6 rounded-xl">
              <div className="text-sm text-gray-400 mb-2">YTD Cost Savings</div>
              <div className="text-4xl font-bold text-teal-400">
                ${(metrics.ytdSavings / 1000000).toFixed(2)}M
              </div>
              <div className="text-xs text-gray-500 mt-2">AI-Driven Optimisation</div>
            </div>
            <div className="glass-card p-6 rounded-xl">
              <div className="text-sm text-gray-400 mb-2">Average ETA Drift</div>
              <div className="text-4xl font-bold text-cyan-400">{metrics.avgETADrift}min</div>
              <div className="text-xs text-gray-500 mt-2">Delay vs. Estimated Arrival</div>
            </div>
            <div className="glass-card p-6 rounded-xl">
              <div className="text-sm text-gray-400 mb-2">Machine Health</div>
              <div className="text-4xl font-bold text-blue-400">{metrics.avgMachineHealth}%</div>
              <div className="text-xs text-gray-500 mt-2">Average Fleet Status</div>
            </div>
          </div>
        </section>

        {/* Risk Assessment */}
        <section className="mb-12">
          <h3 className="text-2xl font-bold text-teal-300 mb-6">Risk Assessment</h3>
          <div className="glass-card p-6 rounded-xl mb-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-sm text-gray-400">Total Active Risks</div>
                <div className="text-3xl font-bold text-rose-400">{metrics.totalRisks}</div>
              </div>
              <div className="flex gap-4 text-sm">
                <div>
                  <div className="text-gray-400">High</div>
                  <div className="text-xl font-bold text-red-400">{metrics.highRisks}</div>
                </div>
                <div>
                  <div className="text-gray-400">Medium</div>
                  <div className="text-xl font-bold text-amber-400">{metrics.mediumRisks}</div>
                </div>
                <div>
                  <div className="text-gray-400">Low</div>
                  <div className="text-xl font-bold text-green-400">{metrics.lowRisks}</div>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-700">
              <div>
                <div className="text-xs text-gray-400 mb-1">Critical Flights</div>
                <div className="text-lg font-semibold">{metrics.criticalFlights}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">Critical Machines</div>
                <div className="text-lg font-semibold">{metrics.criticalMachines}</div>
              </div>
            </div>
          </div>

          {/* Top Risks Table */}
          <div className="glass-card p-6 rounded-xl">
            <h4 className="text-lg font-semibold text-gray-200 mb-4">Top Priority Risks</h4>
            <table className="w-full text-sm">
              <thead className="border-b border-slate-700">
                <tr className="text-left text-gray-400">
                  <th className="pb-2">Flight/Machine</th>
                  <th className="pb-2">Severity</th>
                  <th className="pb-2">Action</th>
                  <th className="pb-2">ROI</th>
                </tr>
              </thead>
              <tbody className="text-gray-300">
                {topRisks.map((risk, index) => (
                  <tr key={risk.id} className="border-b border-slate-800">
                    <td className="py-3">{risk.flightId || risk.machineId}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        risk.severity === RISK_SEVERITY.CRITICAL || risk.severity === RISK_SEVERITY.HIGH
                          ? 'bg-red-500/20 text-red-300'
                          : 'bg-amber-500/20 text-amber-300'
                      }`}>
                        {risk.severity.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 text-xs">{risk.suggestedAction}</td>
                    <td className="py-3 font-semibold text-teal-400">{risk.roi}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* AI Recommendations */}
        <section className="mb-12">
          <h3 className="text-2xl font-bold text-teal-300 mb-6">AI-Powered Recommendations</h3>
          <div className="space-y-4">
            {recommendedActions.map((action, index) => (
              <div key={action.action} className="glass-card p-6 rounded-xl">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-1">{action.action}</h4>
                    <p className="text-sm text-gray-400">{action.description}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-400">Expected ROI</div>
                    <div className="text-2xl font-bold text-teal-400">{action.avgROI}</div>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4 pt-3 border-t border-slate-700">
                  <div>
                    <div className="text-xs text-gray-400">Avg Cost</div>
                    <div className="text-sm font-semibold">{action.avgCost}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Avg Savings</div>
                    <div className="text-sm font-semibold text-green-400">{action.avgSavings}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Success Rate</div>
                    <div className="text-sm font-semibold">{Math.round(action.successRate * 100)}%</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Conclusion */}
        <section className="mb-12">
          <h3 className="text-2xl font-bold text-teal-300 mb-6">Strategic Recommendations</h3>
          <div className="space-y-4 text-gray-300 leading-relaxed">
            <p>
              Based on our AI analysis of current operations, we recommend immediate implementation of the following measures:
            </p>
            <ol className="list-decimal list-inside space-y-2 ml-4">
              <li>
                <strong className="text-white">Expedite critical shipments</strong> with ETA drift exceeding 30 minutes to maintain customer commitments and avoid penalties.
              </li>
              <li>
                <strong className="text-white">Activate backup production capacity</strong> for facilities showing machine health below 75% to prevent production bottlenecks.
              </li>
              <li>
                <strong className="text-white">Optimise routing for high-priority cargo</strong> using our AI-recommended alternative paths, projected to save $87K in the next 30 days.
              </li>
              <li>
                <strong className="text-white">Scale preventive maintenance</strong> across {metrics.criticalMachines} critical machines to improve overall fleet health.
              </li>
            </ol>
            <p className="pt-4">
              These actions are projected to improve OTIF performance by <strong className="text-teal-400">+4.2%</strong> and 
              generate an additional <strong className="text-teal-400">${(FINANCIAL_DATA.monthlyTargets.aiSavings / 1000).toFixed(0)}K</strong> in 
              monthly cost savings.
            </p>
          </div>
        </section>

        {/* Footer */}
        <div className="pt-8 border-t border-slate-700 text-center text-xs text-gray-500">
          <p>This document contains confidential and proprietary information.</p>
          <p className="mt-2">© {new Date().getFullYear()} AeroLine Operations. All rights reserved.</p>
          <p className="mt-2">Generated by Snowflake Cortex AI · Digital Twin Platform</p>
        </div>
      </div>
    </div>
  );
}

