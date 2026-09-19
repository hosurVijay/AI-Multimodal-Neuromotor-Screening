import { useState } from "react";
import { registerPatient } from "../services/api";

function AddPatient({ onBack, onPatientRegistered }) {
  const [formData, setFormData] = useState({
    fullName: "",
    dateOfBirth: "",
    gender: "MALE",
    phone: "",
    heightCm: "",
    weightKg: "",
    emergencyContact: "",
    city: "",
    state: "",
    pincode: "",
    neurologicalDisorder: "",
    strokeHistory: false,
    headInjury: false,
    brainInjury: false,
    diabetes: false,
    hypertension: false,
    medications: "",
  });

  const [profileImage, setProfileImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfileImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // Validations
    if (!formData.fullName.trim()) {
      setError("Full Name is required.");
      return;
    }
    if (!formData.dateOfBirth) {
      setError("Date of birth is required.");
      return;
    }
    if (!formData.phone.trim()) {
      setError("Phone number is required.");
      return;
    }

    setLoading(true);

    try {
      const payload = {
        fullName: formData.fullName,
        dateOfBirth: formData.dateOfBirth,
        gender: formData.gender,
        phone: formData.phone,
        heightCm: formData.heightCm ? parseFloat(formData.heightCm) : null,
        weightKg: formData.weightKg ? parseFloat(formData.weightKg) : null,
        emergencyContact: formData.emergencyContact,
        city: formData.city,
        state: formData.state,
        pincode: formData.pincode,
        neurologicalDisorder: formData.neurologicalDisorder || null,
        strokeHistory: formData.strokeHistory,
        headInjury: formData.headInjury,
        brainInjury: formData.brainInjury,
        diabetes: formData.diabetes,
        hypertension: formData.hypertension,
        medications: formData.medications || null,
      };

      const result = await registerPatient(payload, profileImage);
      setSuccess(typeof result === "string" ? result : "Patient registered successfully!");
      
      setTimeout(() => {
        if (onPatientRegistered) {
          onPatientRegistered();
        }
      }, 1200);
    } catch (err) {
      setError(err.message || "Failed to register patient. Please check your inputs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto", paddingBottom: "40px" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "24px" }}>
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
            Register New Patient
          </h2>
          <p style={{ fontSize: "14px", color: "#64748b", marginTop: "4px", margin: 0 }}>
            Fill in the details below to add a new patient to the screening database.
          </p>
        </div>
      </div>

      {error && (
        <div style={{ padding: "14px 18px", borderRadius: "10px", background: "#fef2f2", color: "#b91c1c", border: "1px solid #fecaca", marginBottom: "20px", fontSize: "14px" }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{ padding: "14px 18px", borderRadius: "10px", background: "#f0fdf4", color: "#15803d", border: "1px solid #bbf7d0", marginBottom: "20px", fontSize: "14px" }}>
          ✓ {success}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Section 1: Personal Details */}
        <div style={{ background: "white", borderRadius: "16px", padding: "28px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)", border: "1px solid #f1f5f9", marginBottom: "24px" }}>
          <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#0f172a", marginBottom: "20px", display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#0e7490" }}></span>
            Personal Information
          </h3>

          {/* Profile Image Upload */}
          <div style={{ display: "flex", alignItems: "center", gap: "20px", marginBottom: "24px" }}>
            <div
              style={{
                width: "72px",
                height: "72px",
                borderRadius: "50%",
                background: "#f1f5f9",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                overflow: "hidden",
                border: "2px dashed #cbd5e1",
              }}
            >
              {imagePreview ? (
                <img src={imagePreview} alt="Preview" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              ) : (
                <span style={{ fontSize: "28px", color: "#94a3b8" }}>👤</span>
              )}
            </div>
            <div>
              <label style={{ display: "inline-block", padding: "8px 16px", background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "8px", fontSize: "13px", fontWeight: 500, color: "#334155", cursor: "pointer" }}>
                Upload Profile Picture
                <input type="file" accept="image/*" onChange={handleImageChange} style={{ display: "none" }} />
              </label>
              <p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "4px" }}>JPG, PNG or WEBP (Optional)</p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "18px" }}>
            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                Full Name *
              </label>
              <input
                type="text"
                name="fullName"
                required
                placeholder="e.g. John Doe"
                value={formData.fullName}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                Date of Birth *
              </label>
              <input
                type="date"
                name="dateOfBirth"
                required
                value={formData.dateOfBirth}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                Gender *
              </label>
              <select
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box", background: "white" }}
              >
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                Phone Number *
              </label>
              <input
                type="tel"
                name="phone"
                required
                placeholder="e.g. +91 9876543210"
                value={formData.phone}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                Height (cm)
              </label>
              <input
                type="number"
                step="0.1"
                name="heightCm"
                placeholder="e.g. 175.5"
                value={formData.heightCm}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                Weight (kg)
              </label>
              <input
                type="number"
                step="0.1"
                name="weightKg"
                placeholder="e.g. 70.0"
                value={formData.weightKg}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                Emergency Contact
              </label>
              <input
                type="text"
                name="emergencyContact"
                placeholder="Name / Phone"
                value={formData.emergencyContact}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                City
              </label>
              <input
                type="text"
                name="city"
                placeholder="e.g. Bangalore"
                value={formData.city}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                State
              </label>
              <input
                type="text"
                name="state"
                placeholder="e.g. Karnataka"
                value={formData.state}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
                Pincode
              </label>
              <input
                type="text"
                name="pincode"
                placeholder="e.g. 560001"
                value={formData.pincode}
                onChange={handleChange}
                style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
              />
            </div>
          </div>
        </div>

        {/* Section 2: Medical History */}
        <div style={{ background: "white", borderRadius: "16px", padding: "28px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)", border: "1px solid #f1f5f9", marginBottom: "24px" }}>
          <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#0f172a", marginBottom: "20px", display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#0e7490" }}></span>
            Medical History
          </h3>

          <div style={{ marginBottom: "18px" }}>
            <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
              Known Neurological Disorder
            </label>
            <input
              type="text"
              name="neurologicalDisorder"
              placeholder="e.g. Parkinson's, Tremor, None"
              value={formData.neurologicalDisorder}
              onChange={handleChange}
              style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box" }}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "14px", marginBottom: "20px" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "14px", color: "#334155", cursor: "pointer" }}>
              <input
                type="checkbox"
                name="strokeHistory"
                checked={formData.strokeHistory}
                onChange={handleChange}
                style={{ width: "16px", height: "16px", accentColor: "#0e7490" }}
              />
              Stroke History
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "14px", color: "#334155", cursor: "pointer" }}>
              <input
                type="checkbox"
                name="headInjury"
                checked={formData.headInjury}
                onChange={handleChange}
                style={{ width: "16px", height: "16px", accentColor: "#0e7490" }}
              />
              Head Injury
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "14px", color: "#334155", cursor: "pointer" }}>
              <input
                type="checkbox"
                name="brainInjury"
                checked={formData.brainInjury}
                onChange={handleChange}
                style={{ width: "16px", height: "16px", accentColor: "#0e7490" }}
              />
              Brain Injury
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "14px", color: "#334155", cursor: "pointer" }}>
              <input
                type="checkbox"
                name="diabetes"
                checked={formData.diabetes}
                onChange={handleChange}
                style={{ width: "16px", height: "16px", accentColor: "#0e7490" }}
              />
              Diabetes
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "14px", color: "#334155", cursor: "pointer" }}>
              <input
                type="checkbox"
                name="hypertension"
                checked={formData.hypertension}
                onChange={handleChange}
                style={{ width: "16px", height: "16px", accentColor: "#0e7490" }}
              />
              Hypertension
            </label>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "13px", fontWeight: 600, color: "#475569", marginBottom: "6px" }}>
              Current Medications
            </label>
            <textarea
              name="medications"
              rows="3"
              placeholder="List current prescription drugs or supplements..."
              value={formData.medications}
              onChange={handleChange}
              style={{ width: "100%", padding: "10px 14px", border: "1px solid #cbd5e1", borderRadius: "8px", fontSize: "14px", outline: "none", boxSizing: "border-box", resize: "vertical" }}
            />
          </div>
        </div>

        {/* Form Actions */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px" }}>
          <button
            type="button"
            onClick={onBack}
            style={{
              padding: "12px 24px",
              background: "#f1f5f9",
              border: "1px solid #cbd5e1",
              borderRadius: "10px",
              fontSize: "14px",
              fontWeight: 600,
              color: "#475569",
              cursor: "pointer",
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "12px 28px",
              background: "#0e7490",
              border: "none",
              borderRadius: "10px",
              fontSize: "14px",
              fontWeight: 600,
              color: "white",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? "Registering..." : "Register Patient"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default AddPatient;
