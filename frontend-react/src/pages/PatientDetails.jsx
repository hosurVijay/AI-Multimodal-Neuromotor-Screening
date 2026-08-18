function PatientDetails({ patient, onBack }) {
  if (!patient) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <p className="text-gray-600">Patient not found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 font-sans">

      {/* ================= HEADER ================= */}
      <div className="bg-white border-b border-gray-200 px-8 py-5">

        <div className="flex items-center justify-between">

          <div className="flex items-center gap-3">

            <div className="w-11 h-11 rounded-xl bg-cyan-700 flex items-center justify-center">
              <span className="text-xl font-bold text-white">
                N
              </span>
            </div>

            <div>
              <h1 className="text-xl font-semibold text-cyan-800">
                NeuroCare
              </h1>

              <p className="text-sm text-gray-500">
                Neuromotor Screening System
              </p>
            </div>

          </div>

        </div>

      </div>


      {/* ================= MAIN CONTENT ================= */}
      <div className="px-8 py-8">

        {/* Back button */}
        <button
          onClick={onBack}
          className="text-cyan-700 font-medium hover:underline mb-6"
        >
          ← Back to Patient Summary
        </button>


        {/* Heading */}
        <div className="mb-6">

          <h2 className="text-3xl font-semibold text-gray-800">
            Patient Details
          </h2>

          <p className="text-gray-500 mt-1">
            Detailed information about the selected patient.
          </p>

        </div>


        {/* ================= PATIENT INFORMATION ================= */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">

          {/* Patient header */}
          <div className="px-6 py-6 border-b border-gray-200 flex items-center gap-5">

            <div className="w-20 h-20 rounded-full bg-cyan-100 flex items-center justify-center">
              <span className="text-3xl font-semibold text-cyan-800">
                {patient.name.charAt(0)}
              </span>
            </div>

            <div>
              <h3 className="text-2xl font-semibold text-gray-800">
                {patient.name}
              </h3>

              <p className="text-gray-500 mt-1">
                Patient ID: {patient.id}
              </p>
            </div>

          </div>


          {/* Details */}
          <div className="p-6">

            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-6">

              {/* Patient ID */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Patient ID
                </p>

                <p className="font-medium text-gray-800">
                  {patient.id}
                </p>
              </div>


              {/* Full Name */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Full Name
                </p>

                <p className="font-medium text-gray-800">
                  {patient.name}
                </p>
              </div>


              {/* Gender */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Gender
                </p>

                <p className="font-medium text-gray-800">
                  {patient.gender || "Not available"}
                </p>
              </div>


              {/* Date of Birth */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Date of Birth
                </p>

                <p className="font-medium text-gray-800">
                  {patient.dateOfBirth || "Not available"}
                </p>
              </div>


              {/* Age */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Age
                </p>

                <p className="font-medium text-gray-800">
                  {patient.age || "Not available"}
                </p>
              </div>


              {/* Phone */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Phone
                </p>

                <p className="font-medium text-gray-800">
                  {patient.phone || "Not available"}
                </p>
              </div>


              {/* Email */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Email
                </p>

                <p className="font-medium text-gray-800">
                  {patient.email || "Not available"}
                </p>
              </div>


              {/* Emergency Contact */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Emergency Contact
                </p>

                <p className="font-medium text-gray-800">
                  {patient.emergencyContact || "Not available"}
                </p>
              </div>


              {/* Address */}
              <div className="md:col-span-2">
                <p className="text-sm text-gray-500 mb-1">
                  Address
                </p>

                <p className="font-medium text-gray-800">
                  {patient.address || "Not available"}
                </p>
              </div>


              {/* City */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  City
                </p>

                <p className="font-medium text-gray-800">
                  {patient.city || patient.place || "Not available"}
                </p>
              </div>


              {/* State */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  State
                </p>

                <p className="font-medium text-gray-800">
                  {patient.state || "Not available"}
                </p>
              </div>


              {/* Pincode */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Pincode
                </p>

                <p className="font-medium text-gray-800">
                  {patient.pincode || "Not available"}
                </p>
              </div>


              {/* Height */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Height
                </p>

                <p className="font-medium text-gray-800">
                  {patient.height || "Not available"}
                </p>
              </div>


              {/* Weight */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Weight
                </p>

                <p className="font-medium text-gray-800">
                  {patient.weight || "Not available"}
                </p>
              </div>


              {/* Registration Date */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Registration Date
                </p>

                <p className="font-medium text-gray-800">
                  {patient.registrationDate || "Not available"}
                </p>
              </div>


              {/* Status */}
              <div>
                <p className="text-sm text-gray-500 mb-1">
                  Status
                </p>

                <span
                  className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                    patient.status === "Active"
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {patient.status}
                </span>
              </div>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default PatientDetails;