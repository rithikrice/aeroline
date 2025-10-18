import React from "react";
import { Outlet, Link } from "react-router-dom";
import { Plane } from "lucide-react";

export default function AppLayout() {
  return (
    <div className="flex flex-col h-screen bg-slate-950 text-white">
      {/* Floating Glassy Header */}
      <header className="floating-header glass-panel glass-liquid glass-elevated glass-ambient glass-flow flex items-center justify-between px-6 gap-4">
        {/* Logo */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          <Plane alt="Logo" className="h-7 w-7" />
          <span className="font-semibold text-base whitespace-nowrap">AeroLine</span>
        </div>

        {/* Navigation */}
        <nav className="flex items-center gap-2 overflow-x-auto no-scrollbar flex-1 justify-center">
          <Link to="/dashboard" className="nav-pill whitespace-nowrap">
            Dashboard
          </Link>
          <Link to="/risk" className="nav-pill whitespace-nowrap">
            Risk Engine
          </Link>
          <Link to="/simulator" className="nav-pill whitespace-nowrap">
            Simulator
          </Link>
          <Link to="/ai" className="nav-pill whitespace-nowrap">
            AI-Recommendation
          </Link>
          <Link to="/map" className="nav-pill whitespace-nowrap">
            Realtime-GeoMap
          </Link>
        </nav>

        {/* User Icon Circle */}
        <div className="w-8 h-8 rounded-full bg-white/90 text-gray-900 flex items-center justify-center cursor-pointer hover:bg-white transition-colors border border-white/30 shadow-lg flex-shrink-0">
          <span className="font-semibold text-sm">S</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 pt-24 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
