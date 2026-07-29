import { NavLink, useNavigate } from 'react-router-dom';
import { 
  Activity, 
  FileText, 
  Settings, 
  LogOut,
} from 'lucide-react';
import '../pages/Dashboard.css';

export default function Sidebar() {
  const navigate = useNavigate();
  
  const handleLogout = () => {
    localStorage.removeItem('medflow_token');
    localStorage.removeItem('medflow_user');
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-container">
          <Activity size={20} color="var(--accent-primary)" />
        </div>
        <div>
          <h2>MedFlow AI</h2>
          <p className="subtitle">ENTERPRISE CLINICAL OS</p>
        </div>
      </div>
      
      <div className="demo-mode-badge">
        <Activity size={14} color="var(--accent-primary)" style={{ marginRight: '6px' }} />
        DEMO MODE ACTIVE
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section">
          <span className="section-label">AI AGENTS</span>
          <NavLink
            to="/dashboard"
            end
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <FileText size={18} />
            <span>Clinical Reports</span>
          </NavLink>
        </div>

        <div className="nav-section">
          <span className="section-label">SYSTEM</span>
          <NavLink
            to="/settings"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Settings size={18} />
            <span>Settings</span>
          </NavLink>
          <button onClick={handleLogout} className="nav-item logout-btn">
            <LogOut size={18} />
            <span>Sign Out</span>
          </button>
        </div>
      </nav>
    </aside>
  );
}
