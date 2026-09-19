function Dashboard({ patients, onViewPatient, onNavigate, onAddPatient }) {
  // Stats derived from patient data — will come from API
  const totalPatients = patients ? patients.length : 0;
  const activePatients = patients ? patients.filter((p) => p.status === "ACTIVE" || p.status === "Active").length : 0;

  // Show only recent patients (first 3)
  const recentPatients = patients ? patients.slice(0, 3) : [];

  return (
    <div>
      {/* ================= STAT CARDS ================= */}
      <div className="stat-cards">

        {/* Total Patients */}
        <div className="stat-card">
          <div className="stat-card-icon patients">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <div>
            <div className="stat-card-value">{totalPatients}</div>
            <div className="stat-card-label">Total Patients</div>
            <button className="stat-card-link teal" onClick={() => onNavigate && onNavigate("patients")}>
              Active patients
            </button>
          </div>
        </div>

        {/* Assessments */}
        <div className="stat-card">
          <div className="stat-card-icon assessments">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <line x1="8" y1="12" x2="16" y2="12" />
              <line x1="12" y1="8" x2="12" y2="16" />
            </svg>
          </div>
          <div>
            <div className="stat-card-value">—</div>
            <div className="stat-card-label">Assessments</div>
            <button className="stat-card-link orange" onClick={() => onNavigate && onNavigate("assessments")}>
              This month
            </button>
          </div>
        </div>

        {/* At Risk */}
        <div className="stat-card">
          <div className="stat-card-icon risk">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
          </div>
          <div>
            <div className="stat-card-value">0</div>
            <div className="stat-card-label">At Risk</div>
            <button className="stat-card-link green" onClick={() => onNavigate && onNavigate("alerts")}>
              Require attention
            </button>
          </div>
        </div>

        {/* Critical Alerts */}
        <div className="stat-card">
          <div className="stat-card-icon alerts">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
            </svg>
          </div>
          <div>
            <div className="stat-card-value">0</div>
            <div className="stat-card-label">Critical Alerts</div>
            <button className="stat-card-link red">
              Immediate action
            </button>
          </div>
        </div>
      </div>


      {/* ================= RECENT PATIENTS TABLE ================= */}
      <div className="data-table-container">

        {/* Table header */}
        <div className="data-table-header">
          <h3>Recent Patients</h3>
          <button className="btn-add-patient" onClick={onAddPatient}>
            + Add New Patient
          </button>
        </div>

        {/* Table */}
        <table className="data-table">
          <thead>
            <tr>
              <th>Patient ID</th>
              <th>Full Name</th>
              <th>Place</th>
              <th>Status</th>
              <th>Last Assessment</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {recentPatients.length > 0 ? (
              recentPatients.map((patient) => (
                <tr key={patient.id || patient.patientId}>
                  <td
                    className="patient-id"
                    onClick={() => onViewPatient && onViewPatient(patient)}
                  >
                    {patient.id || patient.patientId}
                  </td>
                  <td>{patient.name || patient.fullName || "—"}</td>
                  <td>{patient.place || patient.city || "—"}</td>
                  <td>
                    <span className={`status-badge ${
                      (patient.status || "").toUpperCase() === "ACTIVE" ? "active" : "inactive"
                    }`}>
                      {(patient.status || "—").toUpperCase()}
                    </span>
                  </td>
                  <td>{patient.lastAssessment || "—"}</td>
                  <td>
                    <button
                      className="view-btn"
                      onClick={() => onViewPatient && onViewPatient(patient)}
                      title="View patient"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                        <circle cx="12" cy="12" r="3" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" style={{ textAlign: "center", padding: "32px", color: "#94a3b8" }}>
                  No patients found. Add a new patient to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {/* View All link */}
        {recentPatients.length > 0 && (
          <div className="table-footer">
            <button className="view-all-link" onClick={() => onNavigate && onNavigate("patients")}>
              View All Patients →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;