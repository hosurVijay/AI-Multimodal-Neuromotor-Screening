// ================= API CONFIGURATION =================
// Base URL for the backend (proxied via Vite during dev, configurable via env)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

// ================= HELPER: GET AUTH HEADER =================
function getAuthHeaders() {
  const token = localStorage.getItem("accessToken");
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// Helper for multipart requests (no Content-Type — browser sets boundary)
function getAuthHeadersMultipart() {
  const token = localStorage.getItem("accessToken");
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// ================= HELPER: HANDLE RESPONSE =================
async function handleResponse(response, isAuthEndpoint = false) {
  if (!response.ok) {
    let errorMessage = `Error: ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.message || errorData.error || errorMessage;
    } catch {
      // Response body is not JSON
    }

    // Backend proxy failure (backend is offline)
    if (response.status === 502 || response.status === 503 || response.status === 504) {
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("neurocare:backend-offline"));
      }
      throw new Error("Backend server is not reachable. Please connect your Spring Boot backend.");
    }

    // Auto-logout on token expiration (401 Unauthorized or 403 Forbidden on protected routes)
    if (!isAuthEndpoint && (response.status === 401 || response.status === 403)) {
      clearAuthData();
      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new CustomEvent("neurocare:session-expired", {
            detail: { message: "Your session has expired. Please log in again." },
          })
        );
      }
    }

    throw new Error(errorMessage);
  }

  // Some endpoints return plain text
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

/**
 * Check if the Spring Boot backend server is active and reachable.
 * @returns {Promise<boolean>}
 */
export async function checkBackendHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);

    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "__ping__", password: "__ping__" }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    // If server responded (even with 400 Bad Request or 401 Invalid Credentials), backend is ALIVE
    if (res.status === 502 || res.status === 503 || res.status === 504) {
      return false;
    }
    return true;
  } catch {
    return false;
  }
}

// ================================================================
//                        AUTH ENDPOINTS
//                    POST /api/auth/login
//                    POST /api/auth/register
//                    POST /api/auth/forgot-password
//                    POST /api/auth/reset-password
// ================================================================

/**
 * Login with email and password.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{accessToken, tokenType, expiresIn, username, email, role}>}
 */
export async function login(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse(response, true);
}

/**
 * Register a new user (admin/doctor).
 * @param {string} username
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{userId, username, email, role, message}>}
 */
export async function register(username, email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });
  return handleResponse(response, true);
}

/**
 * Request a password reset email.
 * @param {string} email
 * @returns {Promise<string>} - Success message
 */
export async function forgotPassword(email) {
  const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  return handleResponse(response, true);
}

/**
 * Reset password using a token.
 * @param {string} token
 * @param {string} newPassword
 * @returns {Promise<string>} - Success message
 */
export async function resetPassword(token, newPassword) {
  const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, newPassword }),
  });
  return handleResponse(response, true);
}

// ================================================================
//                      PATIENT ENDPOINTS
//                    GET  /api/patients
//                    GET  /api/patients/:id
//                    GET  /api/patients/summary
//                    POST /api/patients/register
//                    GET  /api/patients/report/:patientId
// ================================================================

/**
 * Get all patients (full detail).
 * @returns {Promise<Array<PatientResponse>>}
 */
export async function getAllPatients() {
  const response = await fetch(`${API_BASE_URL}/patients`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

/**
 * Get a single patient by ID.
 * @param {number} patientId
 * @returns {Promise<PatientResponse>}
 */
export async function getPatientById(patientId) {
  const response = await fetch(`${API_BASE_URL}/patients/${patientId}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

/**
 * Get all patients in summary form (id, fullName, place, status).
 * @returns {Promise<Array<{patientId, fullName, place, status}>>}
 */
export async function getPatientsSummary() {
  const response = await fetch(`${API_BASE_URL}/patients/summary`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

/**
 * Register a new patient (with optional profile image).
 * @param {object} patientData - PatientRegistrationRequest fields
 * @param {File|null} profileImage - Optional image file
 * @returns {Promise<string>} - Success message
 */
export async function registerPatient(patientData, profileImage = null) {
  const formData = new FormData();

  // The backend expects a JSON part named "patient"
  formData.append(
    "patient",
    new Blob([JSON.stringify(patientData)], { type: "application/json" })
  );

  if (profileImage) {
    formData.append("profileImage", profileImage);
  }

  const response = await fetch(`${API_BASE_URL}/patients/register`, {
    method: "POST",
    headers: getAuthHeadersMultipart(),
    body: formData,
  });
  return handleResponse(response);
}

/**
 * Get all reports for a patient.
 * @param {number} patientId
 * @returns {Promise<Array<{name, sessionId, reportDate, pdfUrl}>>}
 */
export async function getPatientReports(patientId) {
  const response = await fetch(`${API_BASE_URL}/patients/report/${patientId}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

// ================================================================
//                       REPORT ENDPOINTS
//                    GET /api/report/:reportId
// ================================================================

/**
 * Get a single report by report ID.
 * @param {number} reportId
 * @returns {Promise<{name, sessionId, reportDate, pdfUrl}>}
 */
export async function getReportById(reportId) {
  const response = await fetch(`${API_BASE_URL}/report/${reportId}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

// ================================================================
//                     TOKEN MANAGEMENT
// ================================================================

/**
 * Save login response data to localStorage.
 * @param {object} loginResponse - {accessToken, tokenType, expiresIn, username, email, role}
 */
export function saveAuthData(loginResponse) {
  localStorage.setItem("accessToken", loginResponse.accessToken);
  localStorage.setItem("tokenType", loginResponse.tokenType);
  localStorage.setItem("username", loginResponse.username);
  localStorage.setItem("email", loginResponse.email);
  localStorage.setItem("role", loginResponse.role);
  localStorage.setItem(
    "tokenExpiry",
    String(Date.now() + loginResponse.expiresIn)
  );
}

/**
 * Clear all auth data from localStorage.
 */
export function clearAuthData() {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("tokenType");
  localStorage.removeItem("username");
  localStorage.removeItem("email");
  localStorage.removeItem("role");
  localStorage.removeItem("tokenExpiry");
}

/**
 * Check if user is currently authenticated (token exists and not expired).
 * @returns {boolean}
 */
export function isAuthenticated() {
  const token = localStorage.getItem("accessToken");
  const expiry = localStorage.getItem("tokenExpiry");
  if (!token || !expiry) return false;
  return Date.now() < Number(expiry);
}

/**
 * Get stored user info.
 * @returns {{username: string, email: string, role: string} | null}
 */
export function getStoredUser() {
  const username = localStorage.getItem("username");
  const email = localStorage.getItem("email");
  const role = localStorage.getItem("role");
  if (!username) return null;
  return { username, email, role };
}
