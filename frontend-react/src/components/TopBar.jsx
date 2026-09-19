function TopBar({ username }) {
  const displayName = username || "Doctor";
  const initials = displayName.charAt(0).toUpperCase();

  return (
    <div className="topbar">
      {/* Left side */}
      <div className="topbar-left">
        <p className="welcome-text">Welcome Back,</p>
        <h2>Dr. {displayName}</h2>
        <p>Here's what's happening with your patients today.</p>
      </div>

      {/* Right side */}
      <div className="topbar-right">
        {/* Notification bell */}
        <button className="topbar-notification">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          <span className="topbar-notification-dot"></span>
        </button>

        {/* User info */}
        <div className="topbar-user">
          <div className="topbar-avatar">{initials}</div>
          <span className="topbar-user-name">Dr. {displayName} ▾</span>
        </div>
      </div>
    </div>
  );
}

export default TopBar;
