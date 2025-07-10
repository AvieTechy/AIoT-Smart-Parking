import React from 'react'
import { Car, TrendingUp, TrendingDown, Activity } from 'lucide-react'
import type { DashboardStats } from '../types/types'
import '../styles/stats-cards.css'

interface StatsCardsProps {
  stats: DashboardStats
}

const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  return (
    <div className="stats-cards">
      <div className="stats-card current-vehicles">
        <div className="stats-card-content">
          <div className="stats-icon">
            <Car size={24} />
          </div>
          <div className="stats-info">
            <h3>Current Vehicles</h3>
            <p className="stats-number">{stats.currentVehicles}</p>
          </div>
        </div>
      </div>
      
      <div className="stats-card total-entries">
        <div className="stats-card-content">
          <div className="stats-icon">
            <TrendingUp size={24} />
          </div>
          <div className="stats-info">
            <h3>Total Entries</h3>
            <p className="stats-number">{stats.totalEntries}</p>
          </div>
        </div>
      </div>
      
      <div className="stats-card total-exits">
        <div className="stats-card-content">
          <div className="stats-icon">
            <TrendingDown size={24} />
          </div>
          <div className="stats-info">
            <h3>Total Exits</h3>
            <p className="stats-number">{stats.totalExits}</p>
          </div>
        </div>
      </div>
      
      <div className="stats-card occupancy-rate">
        <div className="stats-card-content">
          <div className="stats-icon">
            <Activity size={24} />
          </div>
          <div className="stats-info">
            <h3>Occupancy Rate</h3>
            <p className="stats-number">{stats.occupancyRate.toFixed(1)}%</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatsCards
