import { useState, useEffect } from "react";
import { getPatientReports } from "../services/api";

function PatientDetails({ patient, onBack }) {
  const [reports, setReports] = useState([]);
  const [loadingReports, setLoadingReports] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [showFullImage, setShowFullImage] = useState(false);

  const patientId = patient?.patientId || patient?.id;

  useEffect(() => {
    if (patientId) {
      fetchReports(patientId);
    }
  }, [patientId]);

  const fetchReports = async (id) => {
    setLoadingReports(true);
    try {
      const data = await getPatientReports(id);
      setReports(Array.isArray(data) ? data : []);
    } catch (err) {
      console.warn("Could not load reports:", err.message);
      setReports([]);
    } finally {
      setLoadingReports(false);
    }
  };

  if (!patient) {
    return (
      <div className="placeholder-page">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
        </svg>
        <h3>Patient not found</h3>
        <p>The requested patient information is not available.</p>
        <button
          onClick={onBack}
          style={{
            marginTop: "16px",
            padding: "8px 16px",
            background: "#0e7490",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          ← Back to Patients
        </button>
      </div>
    );
  }

  // Derive display values — all come from API data
  const fullName = patient.fullName || patient.name || "—";
  const gender = patient.gender || "Not available";
  const dateOfBirth = patient.dateOfBirth || "Not available";
  const age = patient.age ? `${patient.age} years` : "Not available";
  const phone = patient.phone || "Not available";
  const email = patient.email || "Not available";
  const emergencyContact = patient.emergencyContact || "Not available";
  const height = patient.heightCm ? `${patient.heightCm} cm` : (patient.height || "Not available");
  const weight = patient.weightKg ? `${patient.weightKg} kg` : (patient.weight || "Not available");
  const city = patient.city || patient.place || "Not available";
  const state = patient.state || "Not available";
  const pincode = patient.pincode || "Not available";
  const registrationDate = patient.registrationDate || "Not available";
  const status = patient.status || "Active";
  const initial = fullName !== "—" ? fullName.charAt(0).toUpperCase() : "?";
  const profileImage = patient.profileImage;

  return (
    <div>
      {/* Header bar with Back button */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "20px" }}>
        <div>
          <button
            onClick={onBack}
            style={{
              background: "none",
              border: "none",
              color: "#0e7490",
              fontWeight: 600,
              fontSize: "14px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              marginBottom: "8px",
              padding: 0,
            }}
          >
            ← Back to Patients
          </button>
          <h2 style={{ fontSize: "24px", fontWeight: 700, color: "#1e293b", margin: 0 }}>
            Patient Profile
          </h2>
          <p className="patient-detail-subtitle" style={{ margin: "4px 0 0" }}>
            Detailed information and screening history for {fullName}.
          </p>
        </div>
      </div>

      {/* Patient card */}
      <div className="patient-detail-card">
        {/* Header with avatar */}
        <div className="patient-detail-header" style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          {profileImage && !imageError ? (
            <div style={{ position: "relative" }}>
              <img
                src={profileImage}
                alt={fullName}
                onError={() => setImageError(true)}
                onClick={() => setShowFullImage(true)}
                title="Click to expand photo"
                style={{
                  width: "72px",
                  height: "72px",
                  borderRadius: "50%",
                  objectFit: "cover",
                  border: "3px solid #0e7490",
                  boxShadow: "0 2px 8px rgba(14, 116, 144, 0.2)",
                  cursor: "pointer",
                  transition: "transform 0.2s",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.05)")}
                onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
              />
            </div>
          ) : (
            <div className="patient-avatar" style={{ width: "72px", height: "72px", fontSize: "28px" }}>
              {initial}
            </div>
          )}
          <div className="patient-header-info">
            <h3 style={{ fontSize: "22px", margin: "0 0 4px" }}>{fullName}</h3>
            <p style={{ margin: "0 0 8px", color: "#64748b" }}>Patient ID: {patientId || "—"}</p>
            <span
              className={`active-badge ${
                String(status).toUpperCase() === "ACTIVE" ? "" : "inactive"
              }`}
            >
              {String(status).toUpperCase()}
            </span>
          </div>
        </div>

        {/* Detail grid */}
        <div className="patient-detail-grid">
          <div>
            <div className="patient-field-label">Patient ID</div>
            <div className="patient-field-value">{patientId || "—"}</div>
          </div>

          <div>
            <div className="patient-field-label">Full Name</div>
            <div className="patient-field-value">{fullName}</div>
          </div>

          <div>
            <div className="patient-field-label">Gender</div>
            <div className="patient-field-value">{gender}</div>
          </div>

          <div>
            <div className="patient-field-label">Date of Birth</div>
            <div className="patient-field-value">{dateOfBirth}</div>
          </div>

          <div>
            <div className="patient-field-label">Age</div>
            <div className="patient-field-value">{age}</div>
          </div>

          <div>
            <div className="patient-field-label">Phone</div>
            <div className="patient-field-value">{phone}</div>
          </div>

          <div>
            <div className="patient-field-label">Email</div>
            <div className="patient-field-value">{email}</div>
          </div>

          <div>
            <div className="patient-field-label">Emergency Contact</div>
            <div className="patient-field-value">{emergencyContact}</div>
          </div>

          <div>
            <div className="patient-field-label">Height</div>
            <div className="patient-field-value">{height}</div>
          </div>

          <div>
            <div className="patient-field-label">Weight</div>
            <div className="patient-field-value">{weight}</div>
          </div>

          <div>
            <div className="patient-field-label">City</div>
            <div className="patient-field-value">{city}</div>
          </div>

          <div>
            <div className="patient-field-label">State</div>
            <div className="patient-field-value">{state}</div>
          </div>

          <div>
            <div className="patient-field-label">Pincode</div>
            <div className="patient-field-value">{pincode}</div>
          </div>

          <div>
            <div className="patient-field-label">Registration Date</div>
            <div className="patient-field-value">{registrationDate}</div>
          </div>

          {/* Profile Photo in grid */}
          <div>
            <div className="patient-field-label">Profile Photo</div>
            <div className="patient-field-value">
              {profileImage && !imageError ? (
                <button
                  type="button"
                  onClick={() => setShowFullImage(true)}
                  style={{
                    background: "#ecfeff",
                    border: "1px solid #a5f3fc",
                    color: "#0e7490",
                    padding: "4px 10px",
                    borderRadius: "6px",
                    fontSize: "13px",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  📷 View Photo
                </button>
              ) : (
                <span style={{ color: "#94a3b8" }}>No photo uploaded</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Reports Section */}
      <div className="data-table-container" style={{ marginTop: "24px" }}>
        <div className="data-table-header">
          <h3>Assessment Reports ({reports.length})</h3>
        </div>

        {loadingReports ? (
          <div style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>
            Loading reports...
          </div>
        ) : reports.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Report Name</th>
                <th>Session ID</th>
                <th>Report Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((report, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600, color: "#1e293b" }}>{report.name || "Neuromotor Assessment"}</td>
                  <td>#{report.sessionId || "—"}</td>
                  <td>{report.reportDate ? new Date(report.reportDate).toLocaleDateString() : "—"}</td>
                  <td>
                    {report.pdfUrl ? (
                      <a
                        href={report.pdfUrl}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          color: "#0e7490",
                          fontWeight: 600,
                          textDecoration: "none",
                          fontSize: "13px",
                        }}
                      >
                        Download PDF ↗
                      </a>
                    ) : (
                      <span style={{ color: "#94a3b8" }}>No PDF</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ padding: "32px", textAlign: "center", color: "#94a3b8" }}>
            No assessment reports available for this patient yet.
          </div>
        )}
      </div>

      {/* Full Size Image Modal */}
      {showFullImage && profileImage && (
        <div
          onClick={() => setShowFullImage(false)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            backgroundColor: "rgba(0, 0, 0, 0.75)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "white",
              padding: "16px",
              borderRadius: "16px",
              maxWidth: "90vw",
              maxHeight: "90vh",
              textAlign: "center",
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <h4 style={{ margin: 0, fontSize: "16px", color: "#1e293b" }}>{fullName} — Profile Photo</h4>
              <button
                onClick={() => setShowFullImage(false)}
                style={{
                  background: "none",
                  border: "none",
                  fontSize: "20px",
                  cursor: "pointer",
                  color: "#64748b",
                }}
              >
                ✕
              </button>
            </div>
            <img
              src={profileImage}
              alt={fullName}
              style={{
                maxWidth: "100%",
                maxHeight: "75vh",
                borderRadius: "12px",
                objectFit: "contain",
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default PatientDetails;