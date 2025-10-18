import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSpring, animated } from "react-spring";
import confetti from "canvas-confetti";
import { Zap, CheckCircle, TrendingUp, DollarSign, Target, AlertTriangle } from "lucide-react";
import { RISKS, RISK_SEVERITY } from "../data/mockData";

export default function PanicButton({ variant = "default" }) {
  const [isActivated, setIsActivated] = useState(false);
  const [phase, setPhase] = useState("idle"); // idle, countdown, processing, success
  const [countdown, setCountdown] = useState(3);
  const [risksCollapsed, setRisksCollapsed] = useState(0);
  const [showReport, setShowReport] = useState(false);

  // Calculate metrics
  const totalRisks = RISKS.length;
  const highRisks = RISKS.filter(r => 
    r.severity === RISK_SEVERITY.HIGH || r.severity === RISK_SEVERITY.CRITICAL
  ).length;
  const estimatedSavings = 247000; // $247K
  const otifImprovement = 4.2;

  // Animated counter for savings
  const savingsSpring = useSpring({
    number: phase === "success" ? estimatedSavings : 0,
    config: { duration: 2000 }
  });

  // Animated counter for OTIF
  const otifSpring = useSpring({
    number: phase === "success" ? otifImprovement : 0,
    config: { duration: 2000 }
  });

  const handlePanicClick = () => {
    setIsActivated(true);
    setPhase("countdown");
    setCountdown(3);
  };

  useEffect(() => {
    if (phase === "countdown" && countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 800);
      return () => clearTimeout(timer);
    } else if (phase === "countdown" && countdown === 0) {
      setPhase("processing");
    }
  }, [phase, countdown]);

  useEffect(() => {
    if (phase === "processing") {
      // Collapse risks one by one
      let riskCounter = 0;
      const riskInterval = setInterval(() => {
        riskCounter++;
        setRisksCollapsed(riskCounter);
        
        if (riskCounter >= highRisks) {
          clearInterval(riskInterval);
          setTimeout(() => {
            setPhase("success");
            triggerConfetti();
          }, 800);
        }
      }, 400);

      return () => clearInterval(riskInterval);
    }
  }, [phase, highRisks]);

  const triggerConfetti = () => {
    const duration = 3000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };

    function randomInRange(min, max) {
      return Math.random() * (max - min) + min;
    }

    const interval = setInterval(function() {
      const timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        return clearInterval(interval);
      }

      const particleCount = 50 * (timeLeft / duration);

      confetti(Object.assign({}, defaults, {
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
      }));
      confetti(Object.assign({}, defaults, {
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
      }));
    }, 250);
  };

  const handleClose = () => {
    setIsActivated(false);
    setPhase("idle");
    setCountdown(3);
    setRisksCollapsed(0);
    setShowReport(false);
  };

  const handleDownloadReport = () => {
    // Generate a simple text report
    const report = `
AEROLINE EMERGENCY OPTIMISATION REPORT
Generated: ${new Date().toLocaleString()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEFORE OPTIMISATION:
- Active High/Critical Risks: ${highRisks}
- Total Risks: ${totalRisks}
- Estimated Monthly Losses: $${estimatedSavings.toLocaleString()}
- OTIF Performance: Below Target

AFTER OPTIMISATION:
- Risks Mitigated: ${highRisks} ✓
- Critical Issues Resolved: 100%
- Projected Savings: $${estimatedSavings.toLocaleString()}
- OTIF Improvement: +${otifImprovement}%

AI ACTIONS TAKEN:
✓ Expedited ${Math.round(highRisks * 0.4)} priority shipments
✓ Rerouted ${Math.round(highRisks * 0.3)} delayed flights
✓ Activated backup capacity for ${Math.round(highRisks * 0.2)} facilities
✓ Optimised ${Math.round(highRisks * 0.1)} machine maintenance schedules

IMPACT:
- ROI: 3.8x
- Time Saved: ${Math.round(highRisks * 2.3)} hours
- Customer Penalties Avoided: $${Math.round(estimatedSavings * 0.4).toLocaleString()}
- Revenue Protected: $${Math.round(estimatedSavings * 1.8).toLocaleString()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Powered by Snowflake Cortex AI | AeroLine Digital Twin
    `;

    const blob = new Blob([report], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `AeroLine_Emergency_Optimisation_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      {/* The Panic Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handlePanicClick}
        className={`
          relative overflow-hidden font-bold rounded-xl shadow-2xl
          ${variant === "large" 
            ? "px-8 py-4 text-lg" 
            : "px-6 py-3 text-base"
          }
          ${isActivated 
            ? "bg-gray-700 cursor-not-allowed" 
            : "bg-gradient-to-r from-red-600 via-red-500 to-orange-500 hover:from-red-500 hover:via-red-400 hover:to-orange-400"
          }
          text-white transition-all duration-300
        `}
        disabled={isActivated}
      >
        <motion.div
          animate={{
            boxShadow: isActivated 
              ? "0 0 0px rgba(239, 68, 68, 0)" 
              : [
                  "0 0 20px rgba(239, 68, 68, 0.5)",
                  "0 0 40px rgba(239, 68, 68, 0.8)",
                  "0 0 20px rgba(239, 68, 68, 0.5)"
                ]
          }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="absolute inset-0 rounded-xl"
        />
        <span className="relative z-10 flex items-center gap-2">
          <Zap className="w-5 h-5" />
          {isActivated ? "Optimising..." : "🚨 OPTIMISE EVERYTHING NOW"}
        </span>
      </motion.button>

      {/* Full-Screen Takeover */}
      <AnimatePresence>
        {isActivated && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[9999] flex items-center justify-center"
            style={{ 
              background: phase === "countdown" 
                ? "rgba(0, 0, 0, 0.95)" 
                : "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)"
            }}
          >
            {/* COUNTDOWN PHASE */}
            {phase === "countdown" && (
              <motion.div
                key="countdown"
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 1.5, opacity: 0 }}
                transition={{ type: "spring", stiffness: 200 }}
                className="text-center"
              >
                <motion.div
                  animate={{
                    scale: [1, 1.2, 1],
                    rotate: [0, 5, -5, 0]
                  }}
                  transition={{ duration: 0.6 }}
                  className="text-9xl font-black text-red-500 drop-shadow-2xl"
                  style={{ textShadow: "0 0 80px rgba(239, 68, 68, 0.8)" }}
                >
                  {countdown}
                </motion.div>
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-8 text-2xl font-semibold text-white"
                >
                  Initializing Emergency Optimisation...
                </motion.p>
              </motion.div>
            )}

            {/* PROCESSING PHASE */}
            {phase === "processing" && (
              <div className="w-full max-w-4xl px-8 space-y-8">
                <motion.div
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center mb-12"
                >
                  <h2 className="text-5xl font-black text-white mb-4 flex items-center justify-center gap-4">
                    <Zap className="w-12 h-12 text-yellow-400 animate-pulse" />
                    AI OPTIMISATION IN PROGRESS
                  </h2>
                  <p className="text-xl text-gray-300">Analyzing all risks and applying optimal solutions...</p>
                </motion.div>

                {/* Risk Collapse Animation */}
                <div className="glass-card glass-card-glow p-8 rounded-2xl">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                      <AlertTriangle className="w-8 h-8 text-orange-400" />
                      Mitigating Risks
                    </h3>
                    <div className="text-4xl font-black text-teal-400">
                      {risksCollapsed} / {highRisks}
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    {Array.from({ length: highRisks }).map((_, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 1, x: 0, height: "auto" }}
                        animate={
                          index < risksCollapsed
                            ? { opacity: 0, x: -100, height: 0 }
                            : { opacity: 1, x: 0, height: "auto" }
                        }
                        transition={{ duration: 0.3 }}
                        className="flex items-center gap-3 p-3 bg-red-500/20 rounded-lg border border-red-500/30"
                      >
                        {index < risksCollapsed ? (
                          <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                        ) : (
                          <div className="w-5 h-5 border-2 border-red-400 rounded-full flex-shrink-0 animate-pulse" />
                        )}
                        <span className="text-sm text-white">
                          Risk #{index + 1} - {index < risksCollapsed ? "Resolved ✓" : "Processing..."}
                        </span>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Processing Stats */}
                <div className="grid grid-cols-3 gap-6">
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card p-6 rounded-xl text-center"
                  >
                    <div className="text-sm text-gray-400 mb-2">Routes Optimised</div>
                    <div className="text-3xl font-bold text-teal-400">{Math.min(risksCollapsed * 3, highRisks * 3)}</div>
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.4 }}
                    className="glass-card p-6 rounded-xl text-center"
                  >
                    <div className="text-sm text-gray-400 mb-2">Flights Expedited</div>
                    <div className="text-3xl font-bold text-blue-400">{Math.min(risksCollapsed * 2, highRisks * 2)}</div>
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.6 }}
                    className="glass-card p-6 rounded-xl text-center"
                  >
                    <div className="text-sm text-gray-400 mb-2">Penalties Avoided</div>
                    <div className="text-3xl font-bold text-green-400">{Math.min(risksCollapsed, highRisks)}</div>
                  </motion.div>
                </div>
              </div>
            )}

            {/* SUCCESS PHASE */}
            {phase === "success" && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-5xl px-8"
              >
                {/* Success Header */}
                <motion.div
                  initial={{ y: -50, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="text-center mb-12"
                >
                  <motion.div
                    animate={{ rotate: [0, 360] }}
                    transition={{ duration: 0.6 }}
                    className="inline-block mb-6"
                  >
                    <CheckCircle className="w-24 h-24 text-green-400" />
                  </motion.div>
                  <h2 className="text-6xl font-black bg-gradient-to-r from-green-400 to-emerald-400 text-transparent bg-clip-text mb-4">
                    OPTIMISATION COMPLETE 🎉
                  </h2>
                  <p className="text-2xl text-gray-300">All critical risks have been mitigated successfully!</p>
                </motion.div>

                {/* Results Cards */}
                <div className="grid grid-cols-2 gap-8 mb-8">
                  {/* Savings Counter */}
                  <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="glass-card glass-card-glow p-8 rounded-2xl border-2 border-green-500/30"
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <DollarSign className="w-10 h-10 text-green-400" />
                      <h3 className="text-xl font-semibold text-white">Projected Savings</h3>
                    </div>
                    <animated.div className="text-6xl font-black text-green-400">
                      {savingsSpring.number.to(n => `$${Math.floor(n).toLocaleString()}`)}
                    </animated.div>
                    <p className="text-sm text-gray-400 mt-2">Next 30 days</p>
                  </motion.div>

                  {/* OTIF Improvement */}
                  <motion.div
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="glass-card glass-card-glow p-8 rounded-2xl border-2 border-teal-500/30"
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <TrendingUp className="w-10 h-10 text-teal-400" />
                      <h3 className="text-xl font-semibold text-white">OTIF Improvement</h3>
                    </div>
                    <animated.div className="text-6xl font-black text-teal-400">
                      {otifSpring.number.to(n => `+${n.toFixed(1)}%`)}
                    </animated.div>
                    <p className="text-sm text-gray-400 mt-2">Performance boost</p>
                  </motion.div>
                </div>

                {/* Additional Stats */}
                <motion.div
                  initial={{ opacity: 0, y: 50 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="glass-card p-6 rounded-xl mb-8"
                >
                  <h4 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5 text-purple-400" />
                    Optimisation Summary 🎉
                  </h4>
                  <div className="grid grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-white">{highRisks}</div>
                      <div className="text-xs text-gray-400">Risks Resolved</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-white">3.8x</div>
                      <div className="text-xs text-gray-400">ROI</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-white">{Math.round(highRisks * 2.3)}hrs</div>
                      <div className="text-xs text-gray-400">Time Saved</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-white">100%</div>
                      <div className="text-xs text-gray-400">Success Rate</div>
                    </div>
                  </div>
                </motion.div>

                {/* Action Buttons */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.8 }}
                  className="flex gap-4 justify-center"
                >
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleDownloadReport}
                    className="px-8 py-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold flex items-center gap-2 shadow-lg"
                  >
                    <DollarSign className="w-5 h-5" />
                    Download Full Report
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleClose}
                    className="px-8 py-4 rounded-xl glass-button text-white font-semibold shadow-lg"
                  >
                    Back to Dashboard
                  </motion.button>
                </motion.div>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

