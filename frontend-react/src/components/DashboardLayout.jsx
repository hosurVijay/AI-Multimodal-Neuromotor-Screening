import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

function DashboardLayout({ currentPage, onNavigate, onLogout, username, children }) {
  return (
    <div className="dashboard-layout">
      <Sidebar
        currentPage={currentPage}
        onNavigate={onNavigate}
        onLogout={onLogout}
      />

      <div className="dashboard-main">
        <TopBar username={username} />

        <div className="dashboard-content">
          {children}
        </div>
      </div>
    </div>
  );
}

export default DashboardLayout;
