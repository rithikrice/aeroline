/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // scans all your React files
  ],
  theme: {
    extend: {
      colors: {
        navy: "#0A192F", // Deep Navy
        teal: "#14F4C9", // Electric Teal
      },
    },
  },
  plugins: [],
};
