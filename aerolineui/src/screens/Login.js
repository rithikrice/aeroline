import { motion } from "framer-motion";
import { useState } from "react";
import { useNavigate } from "react-router-dom"; // Add this import

export default function Login() {
  const navigate = useNavigate(); // Add this hook
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Add your form submission logic here
    console.log("Form submitted:", formData);
    if (!isSignUp) {
      try {
        navigate("/dashboard");
      } catch (error) {
        console.error("Login failed:", error);
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center relative overflow-hidden">
      {/* ...existing code for background orbs... */}

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1 }}
        className="relative z-10 backdrop-blur-lg bg-white/10 border border-white/20 rounded-2xl shadow-2xl p-10 max-w-2xl text-center flex flex-col items-center justify-center"
      >
        <motion.h1
          className="text-5xl font-extrabold bg-gradient-to-r from-[#00f6ff] to-cyan-400 text-transparent bg-clip-text drop-shadow-lg"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 1 }}
        >
          Welcome to AerolineUI ✈️
        </motion.h1>
        <h2> .</h2>

        <div className="w-full max-w-md rounded-2xl bg-white/10 p-8 shadow-2xl backdrop-blur-md border border-white/20 mx-auto">
          <h1 className="text-3xl font-bold text-teal text-center mb-6">
            {isSignUp ? "Create Account" : "Welcome Back"}
          </h1>
          <p className="text-gray-300 text-center mb-8">
            {isSignUp
              ? "Join AeroLine and unlock smarter operations 🚀"
              : "Sign in to continue to AeroLine"}
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            {isSignUp && (
              <div>
                <input
                  type="text"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  placeholder="Full Name"
                  className="w-full rounded-lg border border-white/20 bg-white/5 p-3 text-white placeholder-gray-400 focus:border-teal focus:ring-2 focus:ring-teal outline-none"
                  required
                />
              </div>
            )}

            <div>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Email"
                className="w-full rounded-lg border border-white/20 bg-white/5 p-3 text-white placeholder-gray-400 focus:border-teal focus:ring-2 focus:ring-teal outline-none"
                required
              />
            </div>

            <div>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Password"
                className="w-full rounded-lg border border-white/20 bg-white/5 p-3 text-white placeholder-gray-400 focus:border-teal focus:ring-2 focus:ring-teal outline-none"
                required
              />
            </div>

            {isSignUp && (
              <div>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  placeholder="Confirm Password"
                  className="w-full rounded-lg border border-white/20 bg-white/5 p-3 text-white placeholder-gray-400 focus:border-teal focus:ring-2 focus:ring-teal outline-none"
                  required
                />
              </div>
            )}

            <button
              type="submit"
              className="w-full rounded-lg bg-gradient-to-r from-teal to-cyan-400 p-3 font-semibold text-navy shadow-lg hover:opacity-90 transition"
            >
              {isSignUp ? "Sign Up" : "Login"}
            </button>
          </form>

          {/* Toggle */}
          <p className="mt-6 text-center text-sm text-gray-300">
            {isSignUp ? "Already have an account? " : "Don't have an account? "}
            <button
              type="button"
              onClick={() => setIsSignUp(!isSignUp)}
              className="text-teal hover:underline"
            >
              {isSignUp ? "Login" : "Sign Up"}
            </button>
          </p>
        </div>

        {/* ...existing code for buttons and navigation... */}
      </motion.div>
    </div>
  );
}
