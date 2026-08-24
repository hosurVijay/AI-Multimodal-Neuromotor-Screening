import { useState } from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ForgotPassword from "./pages/ForgotPassword";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  if (loggedIn) {
    return <Dashboard />;
  }

  if (showForgotPassword) {
    return (
      <ForgotPassword
        onBackToLogin={() => setShowForgotPassword(false)}
      />
    );
  }

  return (
    <Login
      onLogin={() => setLoggedIn(true)}
      onForgotPassword={() => setShowForgotPassword(true)}
    />
  );
}

export default App;