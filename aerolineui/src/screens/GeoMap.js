import React, { useState, useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Polyline, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { Plane, AlertCircle, Clock, Package, Globe as GlobeIcon, Map as MapIcon, Sparkles, Eye } from "lucide-react";
import Globe from "react-globe.gl";
import { motion, AnimatePresence } from "framer-motion";

import { FLIGHTS, AIRPORTS, FACILITIES } from "../data/mockData";
import MatrixMode from "../components/MatrixMode";
import PilotView from "../components/PilotView";

// Convert flights data for the map
const flights = FLIGHTS.reduce((acc, flight) => {
  const fromAirport = AIRPORTS[flight.from];
  const toAirport = AIRPORTS[flight.to];
  
  acc[`${flight.flightNumber} (${flight.from}-${flight.to})`] = {
    flightData: flight,
    path: flight.route,
    timeline: [
      { step: "Flight Departure", time: flight.departure, location: fromAirport?.name },
      { step: "In Transit", time: "Currently tracking...", location: "Over International Waters" },
      { step: "Estimated Arrival", time: flight.estimatedArrival, location: toAirport?.name },
      { step: "Customs Clearance", time: "TBD after arrival", location: toAirport?.name },
      { step: "Facility Integration", time: flight.destinationFacility ? FACILITIES[flight.destinationFacility]?.name : "N/A", location: flight.destinationFacility ? FACILITIES[flight.destinationFacility]?.city : "N/A" },
    ],
    cargo: flight.cargo,
    weight: flight.weight,
    status: flight.status,
    etaDrift: flight.etaDrift,
    priority: flight.priority,
    trackingCode: flight.trackingCode,
  };
  return acc;
}, {});

const flightKeys = Object.keys(flights);

const planeIcon = new L.DivIcon({
  className: "custom-plane",
  html: "✈️",
  iconSize: [30, 30],
  iconAnchor: [15, 15], // Center the icon
});

export default function GeoMap() {
  const [selectedFlight, setSelectedFlight] = useState(flightKeys[0] || "");
  const [planeIndex, setPlaneIndex] = useState(0);
  const [viewMode, setViewMode] = useState("map"); // "map" or "globe"
  const [matrixMode, setMatrixMode] = useState(false);
  const [pilotView, setPilotView] = useState(false);
  const globeEl = useRef();

  const flight = flights[selectedFlight];


  // Prepare globe data for SELECTED FLIGHT ONLY
  const selectedFlightData = flight?.flightData;
  const arcsData = selectedFlightData ? [{
    startLat: AIRPORTS[selectedFlightData.from]?.lat || 0,
    startLng: AIRPORTS[selectedFlightData.from]?.lng || 0,
    endLat: AIRPORTS[selectedFlightData.to]?.lat || 0,
    endLng: AIRPORTS[selectedFlightData.to]?.lng || 0,
    color: selectedFlightData.status === 'critical' ? '#ef4444' : 
           selectedFlightData.status === 'delayed' ? '#f59e0b' : '#14b8a6',
    status: selectedFlightData.status,
    flightNumber: selectedFlightData.flightNumber
  }] : [];

  const pointsData = selectedFlightData ? [
    {
      lat: AIRPORTS[selectedFlightData.from]?.lat || 0,
      lng: AIRPORTS[selectedFlightData.from]?.lng || 0,
      size: 0.5,
      color: selectedFlightData.status === 'critical' ? '#ef4444' : 
             selectedFlightData.status === 'delayed' ? '#f59e0b' : '#14b8a6',
      label: selectedFlightData.from
    },
    {
      lat: AIRPORTS[selectedFlightData.to]?.lat || 0,
      lng: AIRPORTS[selectedFlightData.to]?.lng || 0,
      size: 0.5,
      color: selectedFlightData.status === 'critical' ? '#ef4444' : 
             selectedFlightData.status === 'delayed' ? '#f59e0b' : '#14b8a6',
      label: selectedFlightData.to
    }
  ] : [];

  // Auto-focus and rotate globe on selected flight
  useEffect(() => {
    if (viewMode === "globe" && globeEl.current && selectedFlightData) {
      // Center camera on the flight route
      const fromAirport = AIRPORTS[selectedFlightData.from];
      const toAirport = AIRPORTS[selectedFlightData.to];
      
      if (fromAirport && toAirport) {
        // Calculate midpoint for camera focus
        const midLat = (fromAirport.lat + toAirport.lat) / 2;
        const midLng = (fromAirport.lng + toAirport.lng) / 2;
        
        // Point camera at the route
        setTimeout(() => {
          globeEl.current.pointOfView(
            { lat: midLat, lng: midLng, altitude: 2 },
            1000
          );
        }, 100);
      }
      
      globeEl.current.controls().autoRotate = false;
      globeEl.current.controls().enableZoom = true;
    }
  }, [viewMode, selectedFlight, selectedFlightData]);

  // Animate plane along path
  useEffect(() => {
    if (!flight || !flight.path || flight.path.length === 0) return;
    setPlaneIndex(0);
    const interval = setInterval(() => {
      setPlaneIndex((prev) =>
        prev < flight.path.length - 1 ? prev + 1 : prev
      );
    }, 2000);
    return () => clearInterval(interval);
  }, [selectedFlight, flight?.path?.length]);

  const getStatusColor = (status) => {
    switch(status) {
      case 'critical': return 'text-red-500';
      case 'delayed': return 'text-orange-500';
      case 'on_time': return 'text-green-500';
      default: return 'text-blue-500';
    }
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      urgent: 'bg-red-600',
      high: 'bg-orange-600',
      medium: 'bg-yellow-600',
      low: 'bg-green-600'
    };
    return colors[priority] || 'bg-gray-600';
  };

  if (!flight) {
    return (
      <div className="min-h-screen bg-[#0a0f1f] text-white p-6">
        <header className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-teal-400">AeroLine - Live Flight Tracking</h1>
          <select
            value={selectedFlight}
            onChange={(e) => setSelectedFlight(e.target.value)}
            className="bg-[#11182c] text-white px-4 py-2 rounded-lg border border-teal-400"
          >
            {flightKeys.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </header>
        <div className="bg-[#11182c] p-6 rounded-xl border border-[#1c2a48]">
          No flight data available.
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col p-6">
      {/* Header */}
      <header className="flex items-center justify-between mb-6 flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-teal-400">
            AeroLine - Live Flight Tracking
          </h1>
          <p className="text-sm text-gray-400">Real-time cargo flight monitoring · {Object.keys(flights).length} active flights</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {/* View Toggle */}
          <div className="glass-card rounded-xl p-1 flex gap-1">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setViewMode("map")}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-semibold transition-all ${
                viewMode === "map"
                  ? "bg-teal-500/30 text-teal-300 border border-teal-400/50"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <MapIcon className="w-4 h-4" />
              <span>Map</span>
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setViewMode("globe")}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-semibold transition-all ${
                viewMode === "globe"
                  ? "bg-purple-500/30 text-purple-300 border border-purple-400/50"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <GlobeIcon className="w-4 h-4" />
              <span>Globe</span>
            </motion.button>
          </div>

          {/* Special Modes */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setPilotView(true)}
            className="glass-card px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-semibold text-white border border-cyan-400/50 hover:bg-cyan-500/20 transition"
          >
            <Eye className="w-4 h-4" />
            <span>Pilot View</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setMatrixMode(true)}
            className="glass-card px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-semibold text-white border border-green-400/50 hover:bg-green-500/20 transition"
            title="Enter Matrix Mode"
          >
            <Sparkles className="w-4 h-4" />
            <span>Matrix</span>
          </motion.button>
          
          <select
            value={selectedFlight}
            onChange={(e) => setSelectedFlight(e.target.value)}
            className="glass-card text-white px-4 py-2 rounded-lg border border-teal-400 focus:ring-2 focus:ring-teal-400"
          >
            {Object.keys(flights).map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
        </div>
      </header>

      {/* Flight Info Cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="glass-card p-4 rounded-lg glass-card-glow">
          <div className="flex items-center gap-2 mb-2">
            <Plane className="w-4 h-4 text-teal-400" />
            <span className="text-xs text-gray-400">Status</span>
          </div>
          <p className={`text-lg font-semibold ${getStatusColor(flight.status)}`}>
            {flight.status.replace('_', ' ').toUpperCase()}
          </p>
        </div>
        <div className="glass-card p-4 rounded-lg glass-card-glow">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-teal-400" />
            <span className="text-xs text-gray-400">ETA Drift</span>
          </div>
          <p className={`text-lg font-semibold ${flight.etaDrift > 0 ? 'text-red-400' : 'text-green-400'}`}>
            {flight.etaDrift > 0 ? '+' : ''}{flight.etaDrift} min
          </p>
        </div>
        <div className="glass-card p-4 rounded-lg glass-card-glow">
          <div className="flex items-center gap-2 mb-2">
            <Package className="w-4 h-4 text-teal-400" />
            <span className="text-xs text-gray-400">Cargo Weight</span>
          </div>
          <p className="text-lg font-semibold text-white">{flight.weight}</p>
        </div>
        <div className="glass-card p-4 rounded-lg glass-card-glow">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-4 h-4 text-teal-400" />
            <span className="text-xs text-gray-400">Priority</span>
          </div>
          <span className={`${getPriorityBadge(flight.priority)} px-3 py-1 rounded-full text-xs font-semibold`}>
            {flight.priority.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Content Layout */}
      <div className="flex gap-6 flex-1">
        {/* Map or Globe View */}
        <div className="flex-1 rounded-xl overflow-hidden glass-card glass-card-glow relative">
          {viewMode === "map" ? (
            <MapContainer
              center={flight.path && flight.path.length > 0 ? flight.path[Math.floor(flight.path.length / 2)] : [20, 0]}
              zoom={3}
              style={{ height: "600px", width: "100%" }}
              className="rounded-xl"
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution="&copy; OpenStreetMap contributors"
              />
              {flight.path && flight.path.length > 1 && (
                <Polyline 
                positions={flight.path}
                color={flight.status === 'critical' ? '#ef4444' : flight.status === 'delayed' ? '#f59e0b' : '#14b8a6'} 
                weight={3}
                opacity={0.7}
                />
              )}
              {flight.path && flight.path[planeIndex] && (
                <Marker
                  position={flight.path[planeIndex]}
                  icon={planeIcon}
                >
                  <Popup>
                    <div className="text-gray-900">
                      <strong>{selectedFlight.split(' ')[0]}</strong><br />
                      Status: {flight.status}<br />
                      ETA Drift: {flight.etaDrift} min
                    </div>
                  </Popup>
                </Marker>
              )}
            </MapContainer>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="w-full h-[600px] flex items-center justify-center"
            >
              <Globe
                ref={globeEl}
                globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
                backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
                arcsData={arcsData}
                arcColor="color"
                arcDashLength={0.4}
                arcDashGap={0.2}
                arcDashAnimateTime={2000}
                arcStroke={1}
                arcsTransitionDuration={1000}
                pointsData={pointsData}
                pointColor="color"
                pointAltitude={0.01}
                pointRadius="size"
                pointResolution={12}
                atmosphereColor="#5eead4"
                atmosphereAltitude={0.15}
                width={window.innerWidth > 1400 ? 950 : window.innerWidth * 0.52}
                height={600}
              />
            </motion.div>
          )}
        </div>

        {/* Sidebar */}
        <div className="w-96 space-y-4">
          {/* Timeline */}
          <div className="glass-card p-6 rounded-xl glass-card-glow">
            <h2 className="text-lg font-semibold mb-4">Flight Timeline</h2>
            <ul className="space-y-4">
              {flight.timeline.map((event, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <Plane className={`w-4 h-4 mt-1 ${idx === 0 ? 'text-green-400' : idx === 1 ? 'text-blue-400' : 'text-gray-400'}`} />
                  <div className="flex-1">
                    <p className="text-white font-medium">{event.step}</p>
                    <p className="text-gray-400 text-sm">{event.time}</p>
                    {event.location && <p className="text-gray-500 text-xs mt-1">{event.location}</p>}
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Cargo Details */}
          <div className="glass-card p-6 rounded-xl glass-card-glow">
            <h2 className="text-lg font-semibold mb-4">Cargo Details</h2>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-400 mb-1">Description</p>
                <p className="text-sm text-white">{flight.cargo}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Tracking Code</p>
                <p className="text-sm text-teal-400 font-mono">{flight.trackingCode}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Airline</p>
                <p className="text-sm text-white">{flight.flightData.airline}</p>
              </div>
              {flight.flightData.affectedMachines.length > 0 && (
                <div>
                  <p className="text-xs text-gray-400 mb-1">Affected Machines</p>
                  <div className="flex flex-wrap gap-1">
                    {flight.flightData.affectedMachines.map(m => (
                      <span key={m} className="text-xs bg-red-900/30 text-red-300 px-2 py-1 rounded">{m}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Special Modes Overlays */}
      <AnimatePresence>
        {matrixMode && (
          <MatrixMode 
            onExit={() => setMatrixMode(false)}
            onCommandExecute={(cmd, param) => {
              console.log('Matrix command:', cmd, param);
              // You can add special actions here based on matrix commands
            }}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {pilotView && (
          <PilotView 
            flight={flight}
            onExit={() => setPilotView(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
