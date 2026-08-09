import { useState } from "react";

function Login({ onLogin }) {
  const [showPassword, setShowPassword] = useState(false);
   const handleLogin = () => {
  onLogin();
};

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        overflow: "hidden",
        fontFamily: "Arial, sans-serif",
        backgroundColor: "#ffffff",
      }}
    >
      {/* LEFT SIDE - LOGIN */}
      <div
        style={{
          width: "50%",
          padding: "50px 70px",
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        {/* LOGO */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            marginBottom: "70px",
          }}
        >
          <div
            style={{
              width: "45px",
              height: "45px",
              borderRadius: "10px",
              backgroundColor: "#075e68",
              color: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "24px",
              fontWeight: "bold",
            }}
          >
            N
          </div>

          <span
            style={{
              fontSize: "24px",
              fontWeight: "bold",
              color: "#075e68",
            }}
          >
            NeuroCare
          </span>
        </div>

        {/* HEADING */}
        <h1
          style={{
            fontSize: "40px",
            color: "#222222",
            marginBottom: "12px",
          }}
        >
          Welcome Back!
        </h1>

        <p
          style={{
            fontSize: "17px",
            color: "#666666",
            marginBottom: "40px",
            lineHeight: "1.6",
          }}
        >
          Login to access your dashboard and continue
          <br />
          managing neuromotor assessments.
        </p>

        {/* USERNAME */}
        <label
          style={{
            fontSize: "15px",
            fontWeight: "bold",
            marginBottom: "8px",
            color: "#333333",
          }}
        >
          Username
        </label>

        <input
          type="text"
          placeholder="Enter your username"
          style={{
            width: "100%",
            padding: "16px",
            boxSizing: "border-box",
            border: "1px solid #cccccc",
            borderRadius: "8px",
            fontSize: "16px",
            marginBottom: "25px",
            outline: "none",
          }}
        />

        {/* PASSWORD */}
        <label
          style={{
            fontSize: "15px",
            fontWeight: "bold",
            marginBottom: "8px",
            color: "#333333",
          }}
        >
          Password
        </label>

        <div
          style={{
            position: "relative",
            width: "100%",
          }}
        >
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Enter your password"
            style={{
              width: "100%",
              padding: "16px 50px 16px 16px",
              boxSizing: "border-box",
              border: "1px solid #cccccc",
              borderRadius: "8px",
              fontSize: "16px",
              outline: "none",
            }}
          />

          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            style={{
              position: "absolute",
              right: "12px",
              top: "50%",
              transform: "translateY(-50%)",
              border: "none",
              background: "none",
              cursor: "pointer",
              fontSize: "18px",
            }}
          >
            {showPassword ? "🙈" : "👁️"}
          </button>
        </div>

        {/* FORGOT PASSWORD */}
        <div
          style={{
            textAlign: "right",
            marginTop: "12px",
            marginBottom: "30px",
          }}
        >
          <a
            href="#"
            style={{
              color: "#075e68",
              fontWeight: "bold",
              textDecoration: "none",
            }}
          >
            Forgot Password?
          </a>
        </div>

        {/* LOGIN BUTTON */}
        <button
        onClick={handleLogin}
          style={{
            width: "100%",
            padding: "16px",
            backgroundColor: "#075e68",
            color: "white",
            border: "none",
            borderRadius: "8px",
            fontSize: "17px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          Login
        </button>
      </div>

      {/* RIGHT SIDE */}
      <div
        style={{
          width: "50%",
          backgroundColor: "#064f59",
          color: "white",
          padding: "60px",
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <h1
          style={{
            fontSize: "42px",
            lineHeight: "1.2",
            marginBottom: "25px",
          }}
        >
          Neuromotor
          <br />
          Screening
        </h1>

        <p
          style={{
            fontSize: "18px",
            lineHeight: "1.7",
            color: "#d8f1f3",
            marginBottom: "40px",
          }}
        >
          An intelligent multimodal screening system designed
          to identify early signs of neuromotor disorders through
          multiple assessments.
        </p>

        {/* FEATURE 1 */}
        <div
          style={{
            display: "flex",
            gap: "20px",
            marginBottom: "30px",
          }}
        >
          <div
            style={{
              fontSize: "32px",
              backgroundColor: "#176d76",
              width: "60px",
              height: "60px",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            🧠
          </div>

          <div>
            <h3 style={{ margin: "0 0 8px 0" }}>
              Multimodal Assessment
            </h3>

            <p
              style={{
                margin: 0,
                color: "#c9e6e8",
                lineHeight: "1.5",
              }}
            >
              Analyze gait, balance, hand movements,
              tremor and other motor functions.
            </p>
          </div>
        </div>

        {/* FEATURE 2 */}
        <div
          style={{
            display: "flex",
            gap: "20px",
            marginBottom: "30px",
          }}
        >
          <div
            style={{
              fontSize: "32px",
              backgroundColor: "#176d76",
              width: "60px",
              height: "60px",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            📊
          </div>

          <div>
            <h3 style={{ margin: "0 0 8px 0" }}>
              AI-Based Analysis
            </h3>

            <p
              style={{
                margin: 0,
                color: "#c9e6e8",
                lineHeight: "1.5",
              }}
            >
              Combine multiple assessment results to
              estimate neuromotor risk.
            </p>
          </div>
        </div>

        {/* FEATURE 3 */}
        <div
          style={{
            display: "flex",
            gap: "20px",
          }}
        >
          <div
            style={{
              fontSize: "32px",
              backgroundColor: "#176d76",
              width: "60px",
              height: "60px",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            ❤️
          </div>

          <div>
            <h3 style={{ margin: "0 0 8px 0" }}>
              Early Screening
            </h3>

            <p
              style={{
                margin: 0,
                color: "#c9e6e8",
                lineHeight: "1.5",
              }}
            >
              Support early screening and help users
              understand their assessment results.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;