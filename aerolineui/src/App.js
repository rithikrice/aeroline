import logo from "./logo.svg";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import "./App.css";
import Login from "./screens/Login";
import ExecutiveDashboard from "./screens/HomeScreen";
import RiskDashboard from "./screens/RiskEngine";
import WhatIfSimulator from "./screens/Simulator";
import AIUsage from "./screens/AIScreen";
import GeoMapScreen from "./screens/GeoMap";
import AppLayout from "./screens/AppLayout";
import ExecutiveAIDashboard from "./screens/HomeScreen";
import ExecutiveDashboard2 from "./screens/ExecutiveDashboard";
import CinematicTwin from "./screens/CinematicTwin";
import ExecutiveBrief from "./screens/ExecutiveBrief";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Route */}
        <Route path="/" element={<Login />} />

        {/* Full-screen routes (no layout) */}
        <Route path="/cinematic-twin" element={<CinematicTwin />} />
        <Route path="/executive-brief" element={<ExecutiveBrief />} />

        {/* Protected Routes inside Layout */}
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<ExecutiveAIDashboard />} />
          {/* <Route path="/risk" element={<RiskDashboard />} /> */}
          <Route path="/risk" element={<ExecutiveDashboard2 />} />
          <Route path="/simulator" element={<WhatIfSimulator />} />
          <Route path="/ai" element={<AIUsage />} />
          <Route path="/map" element={<GeoMapScreen />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
