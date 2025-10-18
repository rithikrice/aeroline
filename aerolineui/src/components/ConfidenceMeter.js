import React from "react";

export default function ConfidenceMeter({ confidence, size = "md", showLabel = true }) {
  const confidencePercent = Math.round(confidence * 100);
  
  const getConfidenceColor = () => {
    if (confidencePercent >= 80) return "confidence-high";
    if (confidencePercent >= 60) return "confidence-medium";
    return "confidence-low";
  };

  const getConfidenceText = () => {
    if (confidencePercent >= 80) return "High";
    if (confidencePercent >= 60) return "Medium";
    return "Low";
  };

  const sizeClasses = {
    sm: "h-1.5",
    md: "h-2",
    lg: "h-3"
  };

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-gray-400">AI Confidence</span>
          <span className={`text-xs font-semibold ${
            confidencePercent >= 80 ? "text-green-400" : 
            confidencePercent >= 60 ? "text-yellow-400" : 
            "text-red-400"
          }`}>
            {confidencePercent}% {getConfidenceText()}
          </span>
        </div>
      )}
      <div className={`confidence-meter ${sizeClasses[size]}`}>
        <div 
          className={`confidence-fill ${getConfidenceColor()}`}
          style={{ width: `${confidencePercent}%` }}
        ></div>
      </div>
    </div>
  );
}

