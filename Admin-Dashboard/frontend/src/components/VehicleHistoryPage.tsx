import React, { useState, useEffect } from 'react'
import VehicleHistory from './VehicleHistory'
import SearchFilters from './SearchFilters'
import apiService from '../services/apiService'
import type { GroupedSession } from '../types/types'
import '../styles/dashboard.css'

const VehicleHistoryPage: React.FC = () => {
  const [groupedSessions, setGroupedSessions] = useState<GroupedSession[]>([])
  const [filteredSessions, setFilteredSessions] = useState<GroupedSession[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        setError(null)

        const grouped = await apiService.getGroupedSessions()
        setGroupedSessions(grouped)
        setFilteredSessions(grouped)

      } catch (err) {
        console.error('Error loading vehicle history:', err)
        setError('Failed to load vehicle history. Please try again.')
        setGroupedSessions([])
        setFilteredSessions([])
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  const handleSearch = async (searchParams: {
    licensePlate?: string
    dateFrom?: Date
    dateTo?: Date
  }) => {
    try {
      let filtered = groupedSessions

      if (searchParams.licensePlate) {
        filtered = filtered.filter(session => 
          session.licensePlate.toLowerCase().includes(searchParams.licensePlate!.toLowerCase())
        )
      }

      if (searchParams.dateFrom) {
        filtered = filtered.filter(session => {
          const sessionDate = session.entryTime || session.exitTime
          return sessionDate && sessionDate >= searchParams.dateFrom!
        })
      }

      if (searchParams.dateTo) {
        filtered = filtered.filter(session => {
          const sessionDate = session.entryTime || session.exitTime
          return sessionDate && sessionDate <= searchParams.dateTo!
        })
      }

      setFilteredSessions(filtered)
    } catch (err) {
      console.error('Search error:', err)
      setError('Failed to search. Please try again.')
    }
  }

  const clearFilters = () => {
    setFilteredSessions(groupedSessions)
  }

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-content">
          <h1>Vehicle History</h1>
          <div className="loading-state">
            <p>Loading vehicle history...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="dashboard-content">
          <h1>Vehicle History</h1>
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
        <h1>Vehicle History</h1>
        <SearchFilters onSearch={handleSearch} onClear={clearFilters} />
        <VehicleHistory sessions={filteredSessions} />
      </div>
    </div>
  )
}

export default VehicleHistoryPage
