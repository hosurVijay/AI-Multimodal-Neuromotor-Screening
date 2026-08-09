function Dashboard() {
  return (
    <div
      style={{
        height: "100vh",
        backgroundColor: "#f5fafa",
        fontFamily: "Arial, sans-serif",
        overflow: "hidden",
      }}
    >
      {/* HEADER */}
      <div
        style={{
          height: "70px",
          backgroundColor: "#075e68",
          color: "white",
          display: "flex",
          alignItems: "center",
          padding: "0 40px",
          boxSizing: "border-box",
        }}
      >
        <h2 style={{ margin: 0 }}>
          NeuroCare
        </h2>

        <div style={{ marginLeft: "auto" }}>
          Welcome User
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div
        style={{
          padding: "50px",
        }}
      >
        <h1 style={{ color: "#075e68" }}>
          Neuromotor Screening Dashboard
        </h1>

        <p
          style={{
            color: "#666",
            fontSize: "17px",
          }}
        >
          Welcome to your neuromotor screening dashboard.
        </p>

        {/* CARDS */}
        <div
          style={{
            display: "flex",
            gap: "25px",
            marginTop: "40px",
          }}
        >
          <div
            style={{
              backgroundColor: "white",
              padding: "30px",
              borderRadius: "12px",
              width: "220px",
              boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
            }}
          >
            <h3>🧠 Assessments</h3>
            <p>View neuromotor assessments.</p>
          </div>

          <div
            style={{
              backgroundColor: "white",
              padding: "30px",
              borderRadius: "12px",
              width: "220px",
              boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
            }}
          >
            <h3>📊 Results</h3>
            <p>View assessment results.</p>
          </div>

          <div
            style={{
              backgroundColor: "white",
              padding: "30px",
              borderRadius: "12px",
              width: "220px",
              boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
            }}
          >
            <h3>🤖 AI Prediction</h3>
            <p>View AI-based risk prediction.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;