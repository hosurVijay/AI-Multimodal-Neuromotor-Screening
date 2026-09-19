import { useState, useEffect } from "react";
import { checkBackendHealth } from "../services/api";

function ServerNotFound({ onRetry, onBypass }) {
  const [checking, setChecking] = useState(false);
  const [lastChecked, setLastChecked] = useState(new Date().toLocaleTimeString());
  const [autoRetryCount, setAutoRetryCount] = useState(0);

  const handleCheck = async () => {
    setChecking(true);
    try {
      const isAlive = await checkBackendHealth();
      setLastChecked(new Date().toLocaleTimeString());
      if (isAlive && onRetry) {
        onRetry();
      }
    } catch {
      setLastChecked(new Date().toLocaleTimeString());
    } finally {
      setChecking(false);
    }
  };

  // Auto-poll every 6 seconds to automatically detect when the user starts backend in IntelliJ
  useEffect(() => {
    const interval = setInterval(async () => {
      setAutoRetryCount((c) => c + 1);
      try {
        const isAlive = await checkBackendHealth();
        if (isAlive && onRetry) {
          onRetry();
        }
      } catch {
        // Still down
      }
    }, 6000);

    return () => clearInterval(interval);
  }, [onRetry]);

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100vw",
        backgroundColor: "#ffffff",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
        color: "#1e293b",
        padding: "24px",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          maxWidth: "680px",
          width: "100%",
          padding: "48px 40px",
        }}
      >
        {/* Header with Info Icon matching the mockup */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "18px",
            borderBottom: "1px solid #e2e8f0",
            paddingBottom: "24px",
            marginBottom: "28px",
          }}
        >
          {/* Info Circle Icon */}
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "50%",
              border: "3px solid #0e7490",
              color: "#0e7490",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "30px",
              fontWeight: "700",
              fontFamily: "Georgia, serif",
              flexShrink: 0,
            }}
          >
            i
          </div>

          <div>
            <h1
              style={{
                fontSize: "36px",
                fontWeight: "400",
                color: "#0f172a",
                margin: 0,
                letterSpacing: "-0.5px",
              }}
            >
              Server not found
            </h1>
            <p
              style={{
                fontSize: "14px",
                color: "#64748b",
                margin: "4px 0 0 0",
              }}
            >
              Backend connection error
            </p>
          </div>
        </div>

        {/* Primary error description */}
        <p
          style={{
            fontSize: "16px",
            color: "#334155",
            lineHeight: "1.6",
            marginBottom: "20px",
          }}
        >
          NeuroCare can’t find the backend server at{" "}
          <strong style={{ color: "#0e7490" }}>http://localhost:8080</strong>.
        </p>

        {/* Troubleshooting Checklist */}
        <ul
          style={{
            fontSize: "14.5px",
            color: "#475569",
            lineHeight: "1.75",
            paddingLeft: "24px",
            marginBottom: "32px",
          }}
        >
          <li style={{ marginBottom: "10px" }}>
            <strong>Backend not connected:</strong> Please run your Spring Boot application in IntelliJ IDEA on port <code>8080</code>.
          </li>
          <li style={{ marginBottom: "10px" }}>
            Make sure your <strong>MySQL database</strong> service is running on <code>localhost:3306</code>.
          </li>
          <li style={{ marginBottom: "10px" }}>
            Verify that your <code>application.properties</code> is properly configured and no other service is blocking port <code>8080</code>.
          </li>
          <li>
            If you are using a proxy or custom port, ensure the backend URL in <code>api.js</code> matches your active server.
          </li>
        </ul>

        {/* Action Buttons & Status */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            flexWrap: "wrap",
          }}
        >
          <button
            type="button"
            onClick={handleCheck}
            disabled={checking}
            style={{
              padding: "10px 28px",
              background: "#0e7490",
              color: "white",
              border: "1px solid #0891b2",
              borderRadius: "6px",
              fontSize: "15px",
              fontWeight: "500",
              cursor: checking ? "not-allowed" : "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
              transition: "background 0.2s",
            }}
            onMouseEnter={(e) => {
              if (!checking) e.currentTarget.style.background = "#155e75";
            }}
            onMouseLeave={(e) => {
              if (!checking) e.currentTarget.style.background = "#0e7490";
            }}
          >
            {checking ? (
              <>
                <span
                  style={{
                    display: "inline-block",
                    width: "14px",
                    height: "14px",
                    border: "2px solid white",
                    borderTopColor: "transparent",
                    borderRadius: "50%",
                    animation: "spin 0.8s linear infinite",
                  }}
                />
                Connecting...
              </>
            ) : (
              "Try Again"
            )}
          </button>

          {onBypass && (
            <button
              type="button"
              onClick={onBypass}
              style={{
                padding: "10px 20px",
                background: "#f1f5f9",
                color: "#475569",
                border: "1px solid #cbd5e1",
                borderRadius: "6px",
                fontSize: "14px",
                fontWeight: "500",
                cursor: "pointer",
              }}
            >
              Continue to UI Preview
            </button>
          )}

          <span
            style={{
              fontSize: "13px",
              color: "#94a3b8",
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              marginLeft: "auto",
            }}
          >
            <span
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#f59e0b",
                display: "inline-block",
              }}
            />
            Auto-checking every 6s... (Last checked: {lastChecked})
          </span>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default ServerNotFound;
