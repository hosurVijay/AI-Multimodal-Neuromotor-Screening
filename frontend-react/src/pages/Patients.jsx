import { useState } from "react";

function Patients({ patients, onViewPatient, onAddPatient }) {
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const patientsPerPage = 10;

  // Filter patients based on search
  const filteredPatients = patients
    ? patients.filter((patient) => {
        const searchLower = search.toLowerCase();
        const name = (patient.fullName || patient.name || "").toLowerCase();
        const id = String(patient.patientId || patient.id || "").toLowerCase();
        const place = (patient.place || patient.city || "").toLowerCase();
        return (
          name.includes(searchLower) ||
          id.includes(searchLower) ||
          place.includes(searchLower)
        );
      })
    : [];

  // Pagination
  const totalPages = Math.ceil(filteredPatients.length / patientsPerPage);
  const startIndex = (currentPage - 1) * patientsPerPage;
  const currentPatients = filteredPatients.slice(
    startIndex,
    startIndex + patientsPerPage
  );

  return (
    <div>
      {/* Page title */}
      <div style={{ marginBottom: "20px" }}>
        <h2 style={{ fontSize: "24px", fontWeight: 700, color: "#1e293b", margin: 0 }}>
          All Patients
        </h2>
        <p style={{ fontSize: "14px", color: "#64748b", marginTop: "4px" }}>
          View and manage all registered patients.
        </p>
      </div>

      {/* Search */}
      <div className="search-container">
        <input
          type="text"
          placeholder="Search by patient ID, name, or place..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setCurrentPage(1);
          }}
          className="search-input"
        />
      </div>

      {/* Table */}
      <div className="data-table-container">

        <div className="data-table-header">
          <h3>
            Patients
            <span style={{ fontSize: "13px", fontWeight: 400, color: "#94a3b8", marginLeft: "12px" }}>
              Showing {currentPatients.length} of {filteredPatients.length}
            </span>
          </h3>
          <button className="btn-add-patient" onClick={onAddPatient}>
            + Add New Patient
          </button>
        </div>

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
            {currentPatients.length > 0 ? (
              currentPatients.map((patient) => (
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
                    <span
                      className={`status-badge ${
                        (patient.status || "").toUpperCase() === "ACTIVE"
                          ? "active"
                          : "inactive"
                      }`}
                    >
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
                      <svg
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                        <circle cx="12" cy="12" r="3" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="6"
                  style={{
                    textAlign: "center",
                    padding: "32px",
                    color: "#94a3b8",
                  }}
                >
                  {search
                    ? "No patients match your search."
                    : "No patients found. Add a new patient to get started."}
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="pagination">
            <div className="pagination-info">
              Page {currentPage} of {totalPages}
            </div>
            <div className="pagination-buttons">
              <button
                className="pagination-btn"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(Math.max(currentPage - 1, 1))}
              >
                ← Previous
              </button>

              {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                (page) => (
                  <button
                    key={page}
                    className={`pagination-btn ${
                      currentPage === page ? "active" : ""
                    }`}
                    onClick={() => setCurrentPage(page)}
                  >
                    {page}
                  </button>
                )
              )}

              <button
                className="pagination-btn"
                disabled={currentPage === totalPages}
                onClick={() =>
                  setCurrentPage(Math.min(currentPage + 1, totalPages))
                }
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Patients;
