// src/components/ui/Button.js
import React from "react";

export const Button = ({ children, onClick, className = "" }) => {
  return (
    <button
      onClick={onClick}
      className={`bg-teal-500 text-white px-4 py-2 rounded hover:bg-teal-600 transition-colors ${className}`}
    >
      {children}
    </button>
  );
};
