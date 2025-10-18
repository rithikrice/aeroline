import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, TrendingUp, Gauge, Navigation, Clock } from 'lucide-react';

export default function PilotView({ flight, onExit }) {
  const [altitude, setAltitude] = useState(35000);
  const [speed, setSpeed] = useState(550);
  const [fuel, setFuel] = useState(75);
  const [clouds, setClouds] = useState([]);

  useEffect(() => {
    // Generate random clouds
    const newClouds = Array.from({ length: 20 }).map(() => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 100 + 50,
      speed: Math.random() * 2 + 1,
    }));
    setClouds(newClouds);

    // Simulate dynamic flight metrics
    const interval = setInterval(() => {
      setAltitude(prev => prev + (Math.random() - 0.5) * 100);
      setSpeed(prev => prev + (Math.random() - 0.5) * 5);
      setFuel(prev => Math.max(0, prev - 0.1));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch(status) {
      case 'critical': return 'text-red-500';
      case 'delayed': return 'text-orange-500';
      default: return 'text-green-500';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[9999]"
      style={{
        background: 'linear-gradient(to bottom, #1a4d8f 0%, #87CEEB 50%, #f0f8ff 100%)',
      }}
    >
      {/* Sky with moving clouds */}
      <div className="absolute inset-0 overflow-hidden">
        {clouds.map((cloud, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-white/40 blur-xl"
            style={{
              left: `${cloud.x}%`,
              top: `${cloud.y}%`,
              width: `${cloud.size}px`,
              height: `${cloud.size * 0.6}px`,
            }}
            animate={{
              x: ['0%', '100%'],
            }}
            transition={{
              duration: cloud.speed * 10,
              repeat: Infinity,
              ease: 'linear',
            }}
          />
        ))}
      </div>

      {/* Cockpit Frame */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Top dashboard */}
        <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-gray-900 to-transparent opacity-80" />
        
        {/* Side panels */}
        <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-gray-900 to-transparent opacity-60" />
        <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-gray-900 to-transparent opacity-60" />
      </div>

      {/* HUD Overlay */}
      <div className="absolute inset-0 pointer-events-none" style={{ fontFamily: 'Courier New, monospace' }}>
        {/* Center Crosshair */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="relative w-32 h-32">
            <div className="absolute top-1/2 left-0 right-0 h-px bg-cyan-400/60" />
            <div className="absolute left-1/2 top-0 bottom-0 w-px bg-cyan-400/60" />
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-4 border-2 border-cyan-400 rounded-full shadow-lg shadow-cyan-500/50" />
          </div>
        </div>

        {/* Top Left - Flight Info */}
        <div className="absolute top-8 left-8 bg-slate-900/95 backdrop-blur-md p-5 rounded-xl border-2 border-cyan-400/70 shadow-2xl shadow-cyan-500/30 pointer-events-auto">
          <div className="text-2xl font-bold mb-3 text-white drop-shadow-lg">{flight?.flightData?.flightNumber}</div>
          <div className="text-sm space-y-2 text-white">
            <div className="flex items-center gap-2">
              <Navigation className="w-4 h-4 text-cyan-400" />
              <span className="font-semibold">{flight?.flightData?.from} → {flight?.flightData?.to}</span>
            </div>
            <div className={`flex items-center gap-2 ${getStatusColor(flight?.flightData?.status)} font-bold`}>
              <AlertTriangle className="w-4 h-4" />
              <span>STATUS: {flight?.flightData?.status?.toUpperCase()}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              <span className="font-semibold">ETA Drift: {flight?.flightData?.etaDrift}min</span>
            </div>
          </div>
        </div>

        {/* Top Right - Flight Metrics */}
        <div className="absolute top-8 right-8 space-y-3 pointer-events-auto">
          {/* Altitude */}
          <div className="bg-slate-900/95 backdrop-blur-md p-5 rounded-xl border-2 border-cyan-400/70 shadow-2xl shadow-cyan-500/30">
            <div className="text-xs text-cyan-300 font-bold mb-1">ALTITUDE</div>
            <div className="text-4xl font-bold text-white drop-shadow-lg">{Math.round(altitude).toLocaleString()}</div>
            <div className="text-xs text-cyan-300 font-semibold">feet</div>
          </div>

          {/* Speed */}
          <div className="bg-slate-900/95 backdrop-blur-md p-5 rounded-xl border-2 border-cyan-400/70 shadow-2xl shadow-cyan-500/30">
            <div className="text-xs text-cyan-300 font-bold mb-1 flex items-center gap-1">
              <Gauge className="w-3 h-3" />
              AIRSPEED
            </div>
            <div className="text-4xl font-bold text-white drop-shadow-lg">{Math.round(speed)}</div>
            <div className="text-xs text-cyan-300 font-semibold">knots</div>
          </div>

          {/* Fuel */}
          <div className="bg-slate-900/95 backdrop-blur-md p-5 rounded-xl border-2 border-cyan-400/70 shadow-2xl shadow-cyan-500/30">
            <div className="text-xs text-cyan-300 font-bold mb-1">FUEL</div>
            <div className="text-4xl font-bold text-white drop-shadow-lg">{Math.round(fuel)}%</div>
            <div className="w-full h-2 bg-gray-800 rounded-full mt-2 border border-gray-700">
              <div 
                className={`h-full rounded-full transition-all shadow-lg ${
                  fuel > 50 ? 'bg-green-500 shadow-green-500/50' : fuel > 25 ? 'bg-yellow-500 shadow-yellow-500/50' : 'bg-red-500 shadow-red-500/50'
                }`}
                style={{ width: `${fuel}%` }}
              />
            </div>
          </div>
        </div>

        {/* Bottom - AI Co-Pilot Messages */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 w-full max-w-2xl px-4 pointer-events-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-slate-900/95 backdrop-blur-md p-5 rounded-xl border-2 border-emerald-400/70 shadow-2xl shadow-emerald-500/30"
          >
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-emerald-500/30 flex items-center justify-center flex-shrink-0 border border-emerald-400">
                <TrendingUp className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="flex-1">
                <div className="text-xs text-emerald-300 font-bold mb-1">AI CO-PILOT RECOMMENDATION</div>
                <div className="text-sm font-semibold text-white">
                  {flight?.flightData?.status === 'delayed' 
                    ? "Recommend expediting route via priority corridor. ETA improvement: 15 minutes. Cost: $3,200."
                    : flight?.flightData?.status === 'critical'
                    ? "URGENT: Weather system ahead. Suggest alternate route. Rerouting initiated. Safety priority."
                    : "Flight path optimal. All systems nominal. Maintain current heading."
                  }
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Exit Button */}
        <button
          onClick={onExit}
          className="absolute top-8 left-1/2 transform -translate-x-1/2 bg-slate-900/95 backdrop-blur-md px-6 py-3 rounded-xl text-white font-bold pointer-events-auto hover:bg-cyan-500/20 transition border-2 border-cyan-400/70 shadow-2xl shadow-cyan-500/30"
        >
          ← Exit Pilot View
        </button>
      </div>

      {/* Horizon Line */}
      <div className="absolute left-0 right-0 top-1/2 h-px bg-emerald-400/30" />
    </motion.div>
  );
}

