import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import Header from './Header'
import StatsCards from './StatsCards'
import VehicleHistory from './VehicleHistory'
import Statistics from './Statistics'
import SearchFilters from './SearchFilters'
import apiService from '../services/apiService'
import type { Vehicle, DashboardStats, SessionResponse } from '../types/types'
import '../styles/dashboard.css'

const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [filteredVehicles, setFilteredVehicles] = useState<Vehicle[]>([])
  const [stats, setStats] = useState<DashboardStats>({
    currentVehicles: 0,
    totalEntries: 0,
    totalExits: 0,
    occupancyRate: 0
  })
  const [activeTab, setActiveTab] = useState<'history' | 'statistics'>('history')

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load real data from API
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Get sessions and convert to vehicle format
        const [inSessions, outSessions, dashboardStats] = await Promise.all([
          apiService.getInSessions(),
          apiService.getOutSessions(),
          apiService.getDashboardStats()
        ])

        // Convert sessions to vehicles for compatibility
        const inVehicles = inSessions.map(session => apiService.sessionToVehicle(session))
        const outVehicles = outSessions.map(session => apiService.sessionToVehicle(session))
        const allVehicles = [...inVehicles, ...outVehicles]

        setVehicles(allVehicles)
        setFilteredVehicles(allVehicles)
        setStats(dashboardStats)

      } catch (err) {
        console.error('Error loading dashboard data:', err)
        setError('Failed to load dashboard data. Please try again.')
        
        // Fallback to empty data
        setVehicles([])
        setFilteredVehicles([])
        setStats({
          currentVehicles: 0,
          totalEntries: 0,
          totalExits: 0,
          occupancyRate: 0
        })
      } finally {
        setLoading(false)
      }
    }

    loadData()

    // Set up polling for real-time updates
    const pollInterval = setInterval(async () => {
      try {
        const newSessionStatus = await apiService.getNewSessionStatus()
        if (newSessionStatus?.status) {
          // Reload data when new sessions are detected
          loadData()
        }
      } catch (err) {
        console.error('Polling error:', err)
      }
    }, 10000) // Poll every 10 seconds

    return () => {
      clearInterval(pollInterval)
    }
  }, [])

  const handleSearch = async (searchParams: {
    licensePlate?: string
    dateFrom?: Date
    dateTo?: Date
  }) => {
    try {
      let filtered = vehicles

      if (searchParams.licensePlate) {
        // Search by plate number using API
        const sessionsWithPlate = await apiService.searchSessionsByPlate(searchParams.licensePlate)
        const vehiclesWithPlate = sessionsWithPlate.map(session => apiService.sessionToVehicle(session))
        filtered = vehiclesWithPlate
      } else {
        filtered = vehicles
      }

      if (searchParams.dateFrom) {
        filtered = filtered.filter(v => 
          v.entryTime >= searchParams.dateFrom!
        )
      }

      if (searchParams.dateTo) {
        filtered = filtered.filter(v => 
          v.entryTime <= searchParams.dateTo!
        )
      }

      setFilteredVehicles(filtered)
    } catch (err) {
      console.error('Search error:', err)
      setError('Failed to search. Please try again.')
    }
  }

  const clearFilters = () => {
    setFilteredVehicles(vehicles)
  }

  return (
    <div className="dashboard">
      <Header user={user} />
      
      <main className="dashboard-main">
        <div className="dashboard-content">
          <h1>Smart Parking Dashboard</h1>
          
          {loading && (
            <div className="loading-state">
              <p>Loading dashboard data...</p>
            </div>
          )}
          
          {error && (
            <div className="error-state">
              <p style={{ color: 'red' }}>{error}</p>
              <button onClick={() => window.location.reload()}>Retry</button>
            </div>
          )}
          
          {!loading && !error && (
            <>
              <StatsCards stats={stats} />
              
              <div className="dashboard-tabs">
                <div className="tab-buttons">
                  <button 
                    className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
                    onClick={() => setActiveTab('history')}
                  >
                    Session History
                  </button>
                  <button 
                    className={`tab-button ${activeTab === 'statistics' ? 'active' : ''}`}
                    onClick={() => setActiveTab('statistics')}
                  >
                    Statistics
                  </button>
                </div>
                
                <div className="tab-content">
                  {activeTab === 'history' && (
                    <>
                      <SearchFilters onSearch={handleSearch} onClear={clearFilters} />
                      <VehicleHistory vehicles={filteredVehicles} />
                    </>
                  )}
                  
                  {activeTab === 'statistics' && (
                    <Statistics vehicles={vehicles} />
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default Dashboard
