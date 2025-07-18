import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { 
  MdDashboard, 
  MdLocalParking, 
  MdAnalytics, 
  MdSettings,
  MdChevronLeft,
  MdChevronRight,
  MdPerson,
  MdLogout
} from 'react-icons/md'
import '../styles/sidebar.css'

interface SidebarProps {
  isCollapsed: boolean
  onToggle: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggle }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <MdDashboard size={20} />,
      path: '/dashboard',
      description: 'Thống kê tổng quan'
    },
    {
      id: 'parking-map',
      label: 'Parking Map',
      icon: <MdLocalParking size={20} />,
      path: '/parking-map',
      description: 'Sơ đồ chỗ đỗ xe'
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: <MdAnalytics size={20} />,
      path: '/analytics',
      description: 'Phân tích dữ liệu'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: <MdSettings size={20} />,
      path: '/settings',
      description: 'Cài đặt hệ thống'
    }
  ]

  const handleNavigation = (path: string) => {
    navigate(path)
  }

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-title">
          {!isCollapsed && <span>Smart Parking</span>}
        </div>
        <button className="sidebar-toggle" onClick={onToggle}>
          {isCollapsed ? <MdChevronRight size={18} /> : <MdChevronLeft size={18} />}
        </button>
      </div>

      <nav className="sidebar-nav">
        <ul className="sidebar-menu">
          {menuItems.map((item) => (
            <li key={item.id} className="sidebar-menu-item">
              <button
                className={`sidebar-menu-button ${
                  location.pathname === item.path ? 'active' : ''
                }`}
                onClick={() => handleNavigation(item.path)}
                title={isCollapsed ? item.description : ''}
              >
                <span className="sidebar-icon">{item.icon}</span>
                {!isCollapsed && (
                  <span className="sidebar-label">{item.label}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        {/* User Info */}
        <div className="sidebar-user">
          <div className="user-avatar">
            <MdPerson size={isCollapsed ? 20 : 24} />
          </div>
          {!isCollapsed && (
            <div className="user-details">
              <div className="user-name">{user?.username || 'Admin'}</div>
              <div className="user-role">Administrator</div>
            </div>
          )}
        </div>
        
        {/* Logout Button */}
        <button 
          className="logout-button" 
          onClick={logout}
          title={isCollapsed ? 'Logout' : ''}
        >
          <MdLogout size={18} />
          {!isCollapsed && <span>Logout</span>}
        </button>
        
        {/* Version */}
        {!isCollapsed && (
          <div className="sidebar-version-info">
            <p className="sidebar-version">v1.0.0</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Sidebar
