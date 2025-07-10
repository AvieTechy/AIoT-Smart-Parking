import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import { LogOut, User } from 'lucide-react'
import '../styles/header.css'

interface User {
  id: string
  username: string
  email: string
}

interface HeaderProps {
  user: User | null
}

const Header: React.FC<HeaderProps> = ({ user }) => {
  const { logout } = useAuth()

  const handleLogout = () => {
    logout()
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h2>Smart Parking System</h2>
        </div>
        
        <div className="header-right">
          <div className="user-info">
            <User size={20} />
            <span>{user?.username}</span>
          </div>
          
          <button className="logout-button" onClick={handleLogout}>
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
