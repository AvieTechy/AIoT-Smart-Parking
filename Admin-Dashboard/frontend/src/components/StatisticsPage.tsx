import React, { useState, useEffect } from 'react'
import Statistics from './Statistics'
import apiService from '../services/apiService'
import type { Vehicle } from '../types/types'
import '../styles/dashboard.css'

const StatisticsPage: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Use grouped sessions to avoid counting same vehicle multiple times
        const groupedSessions = await apiService.getGroupedSessions()
        
        // Convert grouped sessions to vehicle format
        const vehicles = groupedSessions.map((session) => ({
          id: session.faceId,
          licensePlate: session.licensePlate,
          faceId: session.faceId,
          entryTime: session.entryTime || new Date(),
          exitTime: session.exitTime,
          status: session.status === 'completed' ? 'exited' as const : 'parked' as const,
          plateUrl: session.plateUrl,
          faceUrl: session.faceUrl,
          gate: session.entryGate || 'In'
        }))

        setVehicles(vehicles)

      } catch (err) {
        console.error('Error loading analytics data:', err)
        setError('Failed to load analytics data. Please try again.')
        setVehicles([])
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-content">
          <h1>Analytics & Statistics</h1>
          <div className="loading-state">
            <p>Loading analytics data...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="dashboard-content">
          <h1>Analytics & Statistics</h1>
          <div className="error-state">
            <p style={{ color: 'red' }}>{error}</p>
            <button onClick={() => window.location.reload()}>Retry</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <div className="dashboard-content">
        <h1>Analytics & Statistics</h1>
        <Statistics vehicles={vehicles} />
      </div>
    </div>
  )
}

export default StatisticsPage
