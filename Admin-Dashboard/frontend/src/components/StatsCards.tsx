import React from 'react'
import { Car, TrendingUp, Zap } from 'lucide-react'
import type { DashboardStats } from '../types/types'
import '../styles/stats-cards.css'

interface StatsCardsProps {
  stats: DashboardStats;
}

const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  const totalSlots = stats.total_slots || 0
  const occupancy = totalSlots ? Math.min(100, Math.round(((stats.current_vehicles)/(totalSlots))*100)) : 0

  return (
    <div className="stats-cards">
      <div className="stats-card current-vehicles">
        <div className="stats-card-content">
          <div className="stats-icon"><Car size={24} /></div>
          <div className="stats-info">
            <h3>Current Vehicles</h3>
            <p className="stats-number">{stats.current_vehicles}</p>
            <small>Occupancy {occupancy}%</small>
            <div className="progress-bar"><div className="progress-fill" style={{width: occupancy+'%'}}></div></div>
          </div>
        </div>
      </div>
      <div className="stats-card total-entries">
        <div className="stats-card-content">
          <div className="stats-icon"><TrendingUp size={24} /></div>
          <div className="stats-info">
            <h3>Total Entries</h3>
            <p className="stats-number">{stats.total_entries}</p>
            <small>All entry sessions</small>
          </div>
        </div>
      </div>
      <div className="stats-card available-slots">
        <div className="stats-card-content">
          <div className="stats-icon"><Zap size={24} /></div>
          <div className="stats-info">
            <h3>Available Slots</h3>
            <p className="stats-number">{stats.available_slots}</p>
            <small>of {totalSlots} total</small>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatsCards
