import React from 'react'
import '../styles/header.css'

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h2>VisPark</h2>
        </div>
        
        <div className="header-right">
          <div className="header-actions">
            {/* Có thể thêm notifications, search, etc. */}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
