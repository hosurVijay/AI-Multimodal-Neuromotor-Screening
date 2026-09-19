import { useState } from "react";

function Login({ onLogin, onForgotPassword, sessionExpiredNotice }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Please enter email and password");
      return;
    }

    setLoading(true);

    try {
      await onLogin({ email, password });
    } catch (err) {
      setError(err.message || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: '100vh', width: '100%', overflow: 'hidden', display: 'flex', fontFamily: "'Inter', sans-serif" }}>

      {/* ================= LEFT SIDE ================= */}
      <div style={{ width: '50%', height: '100%', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 64px' }}>

        <div style={{ width: '100%', maxWidth: '448px' }}>

          {/* Logo */}
          <div className="flex items-center gap-3 mb-14">
            <div className="w-12 h-12 rounded-xl bg-cyan-700 flex items-center justify-center">
              <span className="text-2xl font-bold text-white">N</span>
            </div>

            <h1 className="text-2xl font-semibold text-cyan-700">
              NeuroCare
            </h1>
          </div>

          {/* Heading */}
          <h2 className="text-4xl font-semibold text-gray-800 mb-3">
            Welcome Back!
          </h2>

          <p className="text-gray-500 text-lg mb-10">
            Login to access your dashboard and continue managing assessments.
          </p>

          {/* Session Expired Notice */}
          {sessionExpiredNotice && !error && (
            <div className="mb-4 p-3 rounded-lg bg-amber-50 text-amber-800 text-sm border border-amber-200 flex items-center gap-2">
              <span>⚠️</span>
              <span>{sessionExpiredNotice}</span>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-600 text-sm border border-red-200">
              {error}
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleLogin}>

            {/* Email ID */}
            <div className="mb-6">
              <label className="block text-gray-700 font-medium mb-2">
                Email ID
              </label>

              <input
                type="email"
                placeholder="Enter your email ID"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-4 border border-gray-300 rounded-lg
                           outline-none focus:border-cyan-700 focus:ring-2
                           focus:ring-cyan-100 text-gray-700"
              />
            </div>

            {/* Password */}
            <div className="mb-3">
              <label className="block text-gray-700 font-medium mb-2">
                Password
              </label>

              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-4 border border-gray-300 rounded-lg
                           outline-none focus:border-cyan-700 focus:ring-2
                           focus:ring-cyan-100 text-gray-700"
              />
            </div>

            {/* Forgot Password */}
            <div className="flex justify-end mb-8">
              <button
                type="button"
                onClick={onForgotPassword}
                className="text-cyan-700 font-medium hover:underline"
              >
                Forgot Password?
              </button>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 rounded-lg bg-cyan-800
                         text-white text-lg font-medium
                         hover:bg-cyan-900 transition duration-200
                         disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? "LOGGING IN..." : "LOGIN"}
            </button>

          </form>

        </div>
      </div>


      {/* ================= RIGHT SIDE ================= */}
      <div style={{ width: '50%', height: '100%', background: '#083344', color: 'white', padding: '0 56px', display: 'flex', alignItems: 'center' }}>

        <div style={{ maxWidth: '576px' }}>

          {/* Title */}
          <h2 className="text-5xl font-bold leading-tight mb-6">
            Neuromotor
            <br />
            Screening
          </h2>

          <p className="text-cyan-100 text-lg leading-relaxed mb-10">
            An intelligent multimodal screening system designed
            to identify early signs of neuromotor disorders through
            multiple assessments.
          </p>


          {/* Feature 1 */}
          <div className="flex gap-5 mb-8">

            <div className="w-14 h-14 shrink-0 rounded-full bg-cyan-800
                            flex items-center justify-center text-2xl">
              🧠
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-1">
                Multimodal Assessment
              </h3>

              <p className="text-cyan-100 leading-relaxed">
                Analyze gait, balance, hand tremor, grip strength
                and voice-related parameters.
              </p>
            </div>

          </div>


          {/* Feature 2 */}
          <div className="flex gap-5 mb-8">

            <div className="w-14 h-14 shrink-0 rounded-full bg-cyan-800
                            flex items-center justify-center text-2xl">
              📊
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-1">
                AI-Based Screening
              </h3>

              <p className="text-cyan-100 leading-relaxed">
                Combine multiple assessment results to generate
                an intelligent neuromotor risk prediction.
              </p>
            </div>

          </div>


          {/* Feature 3 */}
          <div className="flex gap-5">

            <div className="w-14 h-14 shrink-0 rounded-full bg-cyan-800
                            flex items-center justify-center text-2xl">
              ❤️
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-1">
                Early Screening
              </h3>

              <p className="text-cyan-100 leading-relaxed">
                Support early identification and monitoring
                of potential neuromotor abnormalities.
              </p>
            </div>

          </div>

        </div>
      </div>

    </div>
  );
}

export default Login;