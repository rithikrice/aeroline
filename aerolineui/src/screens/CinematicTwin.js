import React, { useEffect, useRef, useState } from "react";
import Globe from "react-globe.gl";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { X, Play, Pause } from "lucide-react";
import { FLIGHTS, AIRPORTS } from "../data/mockData";

export default function CinematicTwin() {
  const navigate = useNavigate();
  const globeEl = useRef();
  const [isPlaying, setIsPlaying] = useState(true);
  const [caption, setCaption] = useState("");
  const [currentStep, setCurrentStep] = useState(0);

  // Prepare arc data from flights
  const arcsData = FLIGHTS.filter(f => f.route && f.route.length >= 2).map(flight => {
    const from = AIRPORTS[flight.from];
    const to = AIRPORTS[flight.to];
    
    return {
      startLat: from?.lat || 0,
      startLng: from?.lng || 0,
      endLat: to?.lat || 0,
      endLng: to?.lng || 0,
      color: flight.status === 'critical' ? '#ef4444' : 
             flight.status === 'delayed' ? '#f59e0b' : '#14b8a6',
      status: flight.status,
      flightNumber: flight.flightNumber,
      etaDrift: flight.etaDrift
    };
  });

  // Prepare points for critical/delayed flights
  const pointsData = FLIGHTS.filter(f => f.status === 'critical' || f.status === 'delayed').map(flight => {
    const airport = AIRPORTS[flight.from];
    return {
      lat: airport?.lat || 0,
      lng: airport?.lng || 0,
      size: flight.status === 'critical' ? 0.8 : 0.5,
      color: flight.status === 'critical' ? '#ef4444' : '#f59e0b',
      flightNumber: flight.flightNumber,
      status: flight.status
    };
  });

  // Cinematic sequence script
  const cinematicSequence = [
    {
      time: 0,
      duration: 3000,
      caption: "AeroLine Global Operations - Real-time Digital Twin",
      camera: { lat: 20, lng: 0, altitude: 2.5 }
    },
    {
      time: 3000,
      duration: 4000,
      caption: `${FLIGHTS.length} Active Flights Across 6 Continents`,
      camera: { lat: 30, lng: 40, altitude: 2.2 }
    },
    {
      time: 7000,
      duration: 4000,
      caption: `${pointsData.length} Flights Requiring Attention`,
      camera: { lat: 40, lng: -73, altitude: 1.8 }
    },
    {
      time: 11000,
      duration: 4000,
      caption: "Critical Risk Detected - Flight AX-8472 (JFK→LHR)",
      camera: { lat: 51, lng: -0.45, altitude: 1.2 }
    },
    {
      time: 15000,
      duration: 3000,
      caption: "AI Recommendation: Expedite Priority Routing",
      camera: { lat: 45, lng: -30, altitude: 1.5 }
    },
    {
      time: 18000,
      duration: 3000,
      caption: "Projected ROI: 3.8x | Estimated Savings: $87K",
      camera: { lat: 20, lng: 0, altitude: 2.5 }
    }
  ];

  useEffect(() => {
    if (!globeEl.current || !isPlaying) return;

    // Auto-rotate
    globeEl.current.controls().autoRotate = true;
    globeEl.current.controls().autoRotateSpeed = 0.5;

    // Cinematic sequence
    let timeoutId;
    let intervalId;

    const runSequence = () => {
      cinematicSequence.forEach((step, index) => {
        setTimeout(() => {
          if (!isPlaying) return;
          
          setCaption(step.caption);
          setCurrentStep(index);
          
          // Smooth camera transition
          if (globeEl.current) {
            globeEl.current.pointOfView(
              step.camera,
              step.duration * 0.8
            );
          }
        }, step.time);
      });

      // Loop the sequence
      timeoutId = setTimeout(() => {
        if (isPlaying) {
          setCurrentStep(0);
          runSequence();
        }
      }, 21000);
    };

    runSequence();

    return () => {
      clearTimeout(timeoutId);
      if (intervalId) clearInterval(intervalId);
    };
  }, [isPlaying]);

  return (
    <div className="fixed inset-0 z-50 bg-slate-950">
      {/* Globe */}
      <Globe
        ref={globeEl}
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
        backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
        arcsData={arcsData}
        arcColor="color"
        arcDashLength={0.4}
        arcDashGap={0.2}
        arcDashAnimateTime={2000}
        arcStroke={0.5}
        arcsTransitionDuration={0}
        pointsData={pointsData}
        pointColor="color"
        pointAltitude={0.01}
        pointRadius="size"
        pointResolution={12}
        atmosphereColor="#5eead4"
        atmosphereAltitude={0.15}
        width={window.innerWidth}
        height={window.innerHeight}
      />

      {/* Caption Overlay */}
      <AnimatePresence mode="wait">
        <motion.div
          key={caption}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="absolute bottom-24 left-1/2 transform -translate-x-1/2 glass-card glass-card-glow px-10 py-5 rounded-2xl text-center max-w-3xl border-2 border-teal-400/30"
        >
          <p className="text-2xl font-bold text-white drop-shadow-lg">
            {caption}
          </p>
        </motion.div>
      </AnimatePresence>

      {/* Progress Dots */}
      <div className="absolute bottom-12 left-1/2 transform -translate-x-1/2 flex gap-2">
        {cinematicSequence.map((_, index) => (
          <div
            key={index}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              index === currentStep 
                ? 'bg-teal-400 w-8' 
                : 'bg-teal-400/30'
            }`}
          />
        ))}
      </div>

      {/* Controls */}
      <div className="absolute top-6 left-1/2 transform -translate-x-1/2 flex items-center gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsPlaying(!isPlaying)}
          className="glass-button px-4 py-2 rounded-lg flex items-center gap-2 text-white"
        >
          {isPlaying ? (
            <>
              <Pause className="w-4 h-4" />
              <span>Pause</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Play</span>
            </>
          )}
        </motion.button>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate(-1)}
          className="glass-button px-4 py-2 rounded-lg flex items-center gap-2 text-white"
        >
          <X className="w-4 h-4" />
          <span>Exit</span>
        </motion.button>
      </div>

      {/* Branding */}
      <div className="absolute top-6 left-6 glass-card glass-card-glow px-6 py-3 rounded-xl border border-white/10">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 text-transparent bg-clip-text">
          AeroLine Cinematic Twin
        </h1>
        <p className="text-xs text-gray-300 mt-1">Powered by Snowflake Cortex AI</p>
      </div>

      {/* Stats */}
      <div className="absolute top-6 right-6 glass-card glass-card-glow px-6 py-3 rounded-xl space-y-2 text-white">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-teal-400 animate-pulse"></div>
          <span className="text-sm font-semibold">{FLIGHTS.length} Active Flights</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <span className="text-sm">{FLIGHTS.filter(f => f.status === 'critical').length} Critical</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-orange-500"></div>
          <span className="text-sm">{FLIGHTS.filter(f => f.status === 'delayed').length} Delayed</span>
        </div>
      </div>
    </div>
  );
}

