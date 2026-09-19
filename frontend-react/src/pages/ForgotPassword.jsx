import { useState } from "react";
import { forgotPassword as apiForgotPassword } from "../services/api";

function ForgotPassword({ onBackToLogin }) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (email.trim() === "") {
      setError("Please enter your email ID");
      return;
    }

    setLoading(true);

    try {
      // POST /api/auth/forgot-password
      await apiForgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err.message || "Failed to send reset link. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: '100vh', width: '100%', background: '#083344', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Inter', sans-serif" }}>

      <div className="bg-white w-full rounded-2xl shadow-xl" style={{ maxWidth: '448px', padding: '40px' }}>

        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-10">
          <div className="w-12 h-12 rounded-xl bg-cyan-700 flex items-center justify-center">
            <span className="text-2xl font-bold text-white">
              N
            </span>
          </div>

          <h1 className="text-2xl font-semibold text-cyan-700">
            NeuroCare
          </h1>
        </div>

        {/* Heading */}
        <h2 className="text-3xl font-semibold text-gray-800 text-center mb-3">
          Forgot Password?
        </h2>

        <p className="text-gray-500 text-center mb-8">
          {sent
            ? "A password reset link has been sent to your email."
            : "Enter your registered email ID to reset your password."}
        </p>

        {/* Error message */}
        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-600 text-sm border border-red-200">
            {error}
          </div>
        )}

        {!sent && (
          <>
            {/* Form */}
            <form onSubmit={handleSubmit}>

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
                             outline-none focus:border-cyan-700
                             focus:ring-2 focus:ring-cyan-100
                             text-gray-700"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 rounded-lg bg-cyan-800
                           text-white text-lg font-medium
                           hover:bg-cyan-900 transition duration-200
                           disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? "SENDING..." : "SEND RESET LINK"}
              </button>

            </form>
          </>
        )}

        {/* Back to Login */}
        <button
          type="button"
          onClick={onBackToLogin}
          className="w-full mt-6 text-cyan-700 font-medium hover:underline"
        >
          ← Back to Login
        </button>

      </div>

    </div>
  );
}

export default ForgotPassword;