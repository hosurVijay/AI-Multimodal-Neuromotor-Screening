import { useState, useEffect } from "react";
import "./App.css";

import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import Patients from "./pages/Patients";
import PatientDetails from "./pages/PatientDetails";
import AddPatient from "./pages/AddPatient";
import ServerNotFound from "./pages/ServerNotFound";
import DashboardLayout from "./components/DashboardLayout";

import {
  login as apiLogin,
  saveAuthData,
  clearAuthData,
  isAuthenticated,
  getStoredUser,
  getAllPatients,
  getPatientById,
  getPatientsSummary,
  checkBackendHealth,
} from "./services/api";

function App() {
  // ================= SERVER CONNECTION STATE =================
  const [isServerConnected, setIsServerConnected] = useState(true);

  // ================= AUTH STATE =================
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [userRole, setUserRole] = useState("");
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [sessionExpiredNotice, setSessionExpiredNotice] = useState("");

  // ================= NAVIGATION STATE =================
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [selectedPatient, setSelectedPatient] = useState(null);

  // ================= DATA STATE =================
  const [patients, setPatients] = useState([]);
  const [loadingPatients, setLoadingPatients] = useState(false);

  // ================= INITIAL CHECK & OFFLINE LISTENER =================
  useEffect(() => {
    // Listen for backend-offline event from API interceptor
    const handleBackendOffline = () => {
      setIsServerConnected(false);
    };
    window.addEventListener("neurocare:backend-offline", handleBackendOffline);

    // Initial connectivity check
    checkBackendHealth().then((isAlive) => {
      setIsServerConnected(isAlive);
    });

    return () => {
      window.removeEventListener("neurocare:backend-offline", handleBackendOffline);
    };
  }, []);

  // ================= CHECK EXISTING SESSION ON MOUNT =================
  useEffect(() => {
    if (isAuthenticated()) {
      const user = getStoredUser();
      if (user) {
        setUsername(user.username);
        setUserRole(user.role);
        setIsLoggedIn(true);
      }
    } else {
      clearAuthData();
    }
  }, []);

  // ================= AUTO LOGOUT WHEN TOKEN EXPIRES =================
  useEffect(() => {
    if (!isLoggedIn) return;

    const checkTokenExpiry = () => {
      if (!isAuthenticated()) {
        handleLogout("Your session has expired. Please log in again.");
      }
    };

    // Calculate exact millisecond delay until token expiration
    const expiryTimestamp = Number(localStorage.getItem("tokenExpiry"));
    let timerId = null;

    if (expiryTimestamp) {
      const msLeft = expiryTimestamp - Date.now();
      if (msLeft <= 0) {
        checkTokenExpiry();
        return;
      }
      timerId = setTimeout(() => {
        handleLogout("Your session has expired. Please log in again.");
      }, msLeft);
    }

    // Interval fallback to check every 10 seconds
    const intervalId = setInterval(checkTokenExpiry, 10000);

    // Event listener for 401/403 responses from API calls
    const handleAuthExpiredEvent = (e) => {
      handleLogout(e.detail?.message || "Your session has expired. Please log in again.");
    };
    window.addEventListener("neurocare:session-expired", handleAuthExpiredEvent);

    return () => {
      if (timerId) clearTimeout(timerId);
      clearInterval(intervalId);
      window.removeEventListener("neurocare:session-expired", handleAuthExpiredEvent);
    };
  }, [isLoggedIn]);

  // ================= FETCH PATIENTS WHEN LOGGED IN =================
  useEffect(() => {
    if (isLoggedIn) {
      fetchPatients();
    }
  }, [isLoggedIn]);

  const fetchPatients = async () => {
    setLoadingPatients(true);
    try {
      const data = await getAllPatients();
      setPatients(data);
      setIsServerConnected(true);
    } catch (error) {
      console.error("Failed to fetch patients:", error.message);
      if (error.message.includes("not reachable") || error.message.includes("Failed to fetch")) {
        setIsServerConnected(false);
      } else if (error.message.includes("401") || error.message.includes("403")) {
        handleLogout("Your session has expired. Please log in again.");
      }
    } finally {
      setLoadingPatients(false);
    }
  };

  // ================= AUTH HANDLERS =================
  const handleLogin = async ({ email, password }) => {
    setSessionExpiredNotice("");
    try {
      // Calls POST /api/auth/login
      const response = await apiLogin(email, password);

      // Save JWT + user info to localStorage
      saveAuthData(response);

      setUsername(response.username);
      setUserRole(response.role);
      setIsLoggedIn(true);
      setIsServerConnected(true);
      setCurrentPage("dashboard");
    } catch (error) {
      if (error.message.includes("not reachable") || error.message.includes("Failed to fetch")) {
        setIsServerConnected(false);
      }
      throw error;
    }
  };

  const handleLogout = (reason = "") => {
    clearAuthData();
    setIsLoggedIn(false);
    setUsername("");
    setUserRole("");
    setCurrentPage("dashboard");
    setSelectedPatient(null);
    setPatients([]);
    if (reason) {
      setSessionExpiredNotice(reason);
    }
  };

  // ================= NAVIGATION HANDLERS =================
  const handleNavigate = (page) => {
    setSelectedPatient(null);
    setCurrentPage(page);
  };

  const handleViewPatient = async (patient) => {
    // Fetch full patient details from API
    // GET /api/patients/:patientId
    try {
      const patientId = patient.patientId || patient.id;
      const fullDetails = await getPatientById(patientId);
      setSelectedPatient(fullDetails);
      setCurrentPage("patientDetails");
    } catch (error) {
      console.error("Failed to fetch patient details:", error.message);
      // Fallback: use whatever data we have
      setSelectedPatient(patient);
      setCurrentPage("patientDetails");
    }
  };

  const handleBackFromPatient = () => {
    setSelectedPatient(null);
    setCurrentPage("patients");
  };

  const handleAddPatient = () => {
    setCurrentPage("addPatient");
  };

  const handlePatientRegistered = () => {
    // After successfully registering a patient, refresh the list
    fetchPatients();
    setCurrentPage("patients");
  };

  // ================= RENDER: SERVER OFFLINE =================
  if (!isServerConnected) {
    return (
      <ServerNotFound
        onRetry={async () => {
          const alive = await checkBackendHealth();
          if (alive) {
            setIsServerConnected(true);
            if (isLoggedIn) {
              fetchPatients();
            }
          }
        }}
        onBypass={() => setIsServerConnected(true)}
      />
    );
  }

  // ================= RENDER: AUTH PAGES =================
  if (!isLoggedIn) {
    if (showForgotPassword) {
      return (
        <ForgotPassword
          onBackToLogin={() => setShowForgotPassword(false)}
        />
      );
    }

    return (
      <Login
        onLogin={handleLogin}
        onForgotPassword={() => setShowForgotPassword(true)}
        sessionExpiredNotice={sessionExpiredNotice}
      />
    );
  }

  // ================= RENDER: DASHBOARD PAGES =================
  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return (
          <Dashboard
            patients={patients}
            loading={loadingPatients}
            onViewPatient={handleViewPatient}
            onNavigate={handleNavigate}
            onAddPatient={handleAddPatient}
            userRole={userRole}
          />
        );

      case "patients":
        return (
          <Patients
            patients={patients}
            loading={loadingPatients}
            onViewPatient={handleViewPatient}
            onAddPatient={handleAddPatient}
            onRefresh={fetchPatients}
            userRole={userRole}
          />
        );

      case "patientDetails":
        return (
          <PatientDetails
            patient={selectedPatient}
            onBack={handleBackFromPatient}
          />
        );

      case "addPatient":
        return (
          <AddPatient
            onBack={() => setCurrentPage("patients")}
            onPatientRegistered={handlePatientRegistered}
          />
        );

      case "assessments":
        return (
          <div className="placeholder-page">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
            <h3>Assessments</h3>
            <p>Assessment management will be available here.</p>
          </div>
        );

      case "reports":
        return (
          <div className="placeholder-page">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            <h3>Reports</h3>
            <p>Report generation and viewing will be available here.</p>
          </div>
        );

      case "alerts":
        return (
          <div className="placeholder-page">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            <h3>Alerts</h3>
            <p>Patient alerts and notifications will appear here.</p>
          </div>
        );

      case "settings":
        return (
          <div className="placeholder-page">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            <h3>Settings</h3>
            <p>Application settings will be available here.</p>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <DashboardLayout
      currentPage={currentPage}
      onNavigate={handleNavigate}
      onLogout={handleLogout}
      username={username}
    >
      {renderPage()}
    </DashboardLayout>
  );
}

export default App;