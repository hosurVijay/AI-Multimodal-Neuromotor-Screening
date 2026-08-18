import { useState } from "react";

function ForgotPassword({ onBackToLogin }) {
  const [email, setEmail] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (email.trim() === "") {
      alert("Please enter your email ID");
      return;
    }

    alert("Password reset link will be sent to your email.");
  };

  return (
    <div className="h-screen w-screen bg-cyan-950 flex items-center justify-center font-sans">

      <div className="bg-white w-full max-w-md rounded-2xl shadow-xl p-10">

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
          Enter your registered email ID to reset your password.
        </p>

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
            className="w-full py-4 rounded-lg bg-cyan-800
                       text-white text-lg font-medium
                       hover:bg-cyan-900 transition duration-200"
          >
            SEND RESET LINK
          </button>

        </form>

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