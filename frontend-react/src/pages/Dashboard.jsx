import { useState } from "react";
import PatientDetails from "./PatientDetails";

function Dashboard() {

  // ================= PATIENT DATA =================

  const patients = [
    {
      id: "P001",
      name: "Ananya Sharma",
      place: "Bangalore",
      status: "Active",
      gender: "Female",
      dateOfBirth: "12-05-2002",
      age: 24,
      phone: "9876543210",
      email: "ananya@example.com",
      emergencyContact: "9876500000",
      address: "MG Road",
      city: "Bangalore",
      state: "Karnataka",
      pincode: "560001",
      height: "165 cm",
      weight: "55 kg",
      registrationDate: "10-08-2026",
    },
    {
      id: "P002",
      name: "Rahul Kumar",
      place: "Mysore",
      status: "Active",
      gender: "Male",
      dateOfBirth: "20-03-2000",
      age: 26,
      phone: "9876543211",
      email: "rahul@example.com",
      emergencyContact: "9876500001",
      address: "VV Mohalla",
      city: "Mysore",
      state: "Karnataka",
      pincode: "570002",
      height: "172 cm",
      weight: "68 kg",
      registrationDate: "11-08-2026",
    },
    {
      id: "P003",
      name: "Priya Rao",
      place: "Chennai",
      status: "Inactive",
      gender: "Female",
      dateOfBirth: "15-07-2001",
      age: 25,
      phone: "9876543212",
      email: "priya@example.com",
      emergencyContact: "9876500002",
      address: "Anna Nagar",
      city: "Chennai",
      state: "Tamil Nadu",
      pincode: "600040",
      height: "160 cm",
      weight: "54 kg",
      registrationDate: "12-08-2026",
    },
    {
      id: "P004",
      name: "Arjun Reddy",
      place: "Hyderabad",
      status: "Active",
      gender: "Male",
      dateOfBirth: "10-01-1999",
      age: 27,
      phone: "9876543213",
      email: "arjun@example.com",
      emergencyContact: "9876500003",
      address: "Banjara Hills",
      city: "Hyderabad",
      state: "Telangana",
      pincode: "500034",
      height: "175 cm",
      weight: "72 kg",
      registrationDate: "12-08-2026",
    },
    {
      id: "P005",
      name: "Sneha Patel",
      place: "Mumbai",
      status: "Active",
      gender: "Female",
      dateOfBirth: "25-11-2003",
      age: 22,
      phone: "9876543214",
      email: "sneha@example.com",
      emergencyContact: "9876500004",
      address: "Andheri West",
      city: "Mumbai",
      state: "Maharashtra",
      pincode: "400053",
      height: "162 cm",
      weight: "56 kg",
      registrationDate: "13-08-2026",
    },
    {
      id: "P006",
      name: "Kiran Kumar",
      place: "Bangalore",
      status: "Inactive",
      gender: "Male",
      dateOfBirth: "08-06-1998",
      age: 28,
      phone: "9876543215",
      email: "kiran@example.com",
      emergencyContact: "9876500005",
      address: "Whitefield",
      city: "Bangalore",
      state: "Karnataka",
      pincode: "560066",
      height: "170 cm",
      weight: "70 kg",
      registrationDate: "13-08-2026",
    },
    {
      id: "P007",
      name: "Meera Nair",
      place: "Kochi",
      status: "Active",
      gender: "Female",
      dateOfBirth: "14-02-2000",
      age: 26,
      phone: "9876543216",
      email: "meera@example.com",
      emergencyContact: "9876500006",
      address: "MG Road",
      city: "Kochi",
      state: "Kerala",
      pincode: "682016",
      height: "158 cm",
      weight: "52 kg",
      registrationDate: "14-08-2026",
    },
    {
      id: "P008",
      name: "Vivek Singh",
      place: "Delhi",
      status: "Active",
      gender: "Male",
      dateOfBirth: "05-09-2001",
      age: 24,
      phone: "9876543217",
      email: "vivek@example.com",
      emergencyContact: "9876500007",
      address: "Saket",
      city: "Delhi",
      state: "Delhi",
      pincode: "110017",
      height: "178 cm",
      weight: "74 kg",
      registrationDate: "14-08-2026",
    },
    {
      id: "P009",
      name: "Divya Rao",
      place: "Mangalore",
      status: "Active",
      gender: "Female",
      dateOfBirth: "21-12-2002",
      age: 23,
      phone: "9876543218",
      email: "divya@example.com",
      emergencyContact: "9876500008",
      address: "Kadri",
      city: "Mangalore",
      state: "Karnataka",
      pincode: "575004",
      height: "164 cm",
      weight: "53 kg",
      registrationDate: "15-08-2026",
    },
    {
      id: "P010",
      name: "Rohan Das",
      place: "Kolkata",
      status: "Inactive",
      gender: "Male",
      dateOfBirth: "18-04-1997",
      age: 29,
      phone: "9876543219",
      email: "rohan@example.com",
      emergencyContact: "9876500009",
      address: "Salt Lake",
      city: "Kolkata",
      state: "West Bengal",
      pincode: "700091",
      height: "171 cm",
      weight: "69 kg",
      registrationDate: "15-08-2026",
    },
    {
      id: "P011",
      name: "Neha Sharma",
      place: "Pune",
      status: "Active",
    },
    {
      id: "P012",
      name: "Aditya Kumar",
      place: "Bangalore",
      status: "Active",
    },
  ];


  // ================= STATES =================

  const [currentPage, setCurrentPage] = useState(1);

  const [search, setSearch] = useState("");

  const [selectedPatient, setSelectedPatient] = useState(null);


  // ================= PAGINATION =================

  const patientsPerPage = 10;


  // ================= SEARCH =================

  const filteredPatients = patients.filter((patient) =>
    patient.name.toLowerCase().includes(search.toLowerCase()) ||
    patient.id.toLowerCase().includes(search.toLowerCase()) ||
    patient.place.toLowerCase().includes(search.toLowerCase())
  );


  const totalPages = Math.ceil(
    filteredPatients.length / patientsPerPage
  );


  const startIndex =
    (currentPage - 1) * patientsPerPage;


  const currentPatients = filteredPatients.slice(
    startIndex,
    startIndex + patientsPerPage
  );


  // ================= PATIENT DETAILS =================

  if (selectedPatient) {
    return (
      <PatientDetails
        patient={selectedPatient}
        onBack={() => setSelectedPatient(null)}
      />
    );
  }


  // ================= DASHBOARD =================

  return (
    <div className="min-h-screen bg-slate-100 font-sans">

      {/* HEADER */}
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

          <div className="text-right">

            <p className="text-sm text-gray-500">
              Welcome
            </p>

            <p className="font-medium text-gray-700">
              Administrator
            </p>

          </div>

        </div>

      </div>


      {/* MAIN CONTENT */}
      <div className="px-8 py-8">

        <div className="mb-6">

          <h2 className="text-3xl font-semibold text-gray-800">
            Patient Summary
          </h2>

          <p className="text-gray-500 mt-1">
            View and manage registered patients.
          </p>

        </div>


        {/* SEARCH */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 mb-6">

          <input
            type="text"
            placeholder="Search by patient ID, name or place..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full max-w-md px-4 py-3 border border-gray-300
                       rounded-lg outline-none focus:border-cyan-700
                       focus:ring-2 focus:ring-cyan-100"
          />

        </div>


        {/* TABLE */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">

          <div className="px-6 py-5 border-b border-gray-200">

            <h3 className="text-lg font-semibold text-gray-800">
              Patients
            </h3>

            <p className="text-sm text-gray-500 mt-1">
              Showing {currentPatients.length} of {filteredPatients.length} patients
            </p>

          </div>


          <div className="overflow-x-auto">

            <table className="w-full">

              <thead>

                <tr className="bg-gray-50 text-left">

                  <th className="px-6 py-4 text-sm font-semibold text-gray-600">
                    Patient ID
                  </th>

                  <th className="px-6 py-4 text-sm font-semibold text-gray-600">
                    Full Name
                  </th>

                  <th className="px-6 py-4 text-sm font-semibold text-gray-600">
                    Place
                  </th>

                  <th className="px-6 py-4 text-sm font-semibold text-gray-600">
                    Status
                  </th>

                  <th className="px-6 py-4 text-sm font-semibold text-gray-600">
                    Action
                  </th>

                </tr>

              </thead>


              <tbody>

                {currentPatients.map((patient) => (

                  <tr
                    key={patient.id}
                    className="border-t border-gray-100 hover:bg-cyan-50 transition"
                  >

                    <td className="px-6 py-4 font-medium text-cyan-800">
                      {patient.id}
                    </td>

                    <td className="px-6 py-4 text-gray-700">
                      {patient.name}
                    </td>

                    <td className="px-6 py-4 text-gray-600">
                      {patient.place}
                    </td>

                    <td className="px-6 py-4">

                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          patient.status === "Active"
                            ? "bg-green-100 text-green-700"
                            : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {patient.status}
                      </span>

                    </td>

                    <td className="px-6 py-4">

                      <button
                        onClick={() => setSelectedPatient(patient)}
                        className="text-cyan-700 font-medium hover:underline"
                      >
                        View Details
                      </button>

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>


          {/* PAGINATION */}
          <div className="px-6 py-5 border-t border-gray-200 flex items-center justify-between">

            <p className="text-sm text-gray-500">
              Page {currentPage} of {totalPages || 1}
            </p>


            <div className="flex items-center gap-2">

              <button
                onClick={() =>
                  setCurrentPage(Math.max(currentPage - 1, 1))
                }
                disabled={currentPage === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg
                           text-sm font-medium disabled:opacity-40
                           disabled:cursor-not-allowed hover:bg-gray-50"
              >
                ← Previous
              </button>


              {Array.from(
                { length: totalPages },
                (_, index) => index + 1
              ).map((page) => (

                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`w-10 h-10 rounded-lg text-sm font-medium ${
                    currentPage === page
                      ? "bg-cyan-800 text-white"
                      : "border border-gray-300 text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {page}
                </button>

              ))}


              <button
                onClick={() =>
                  setCurrentPage(
                    Math.min(currentPage + 1, totalPages)
                  )
                }
                disabled={
                  currentPage === totalPages ||
                  totalPages === 0
                }
                className="px-4 py-2 border border-gray-300 rounded-lg
                           text-sm font-medium disabled:opacity-40
                           disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Next →
              </button>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default Dashboard;