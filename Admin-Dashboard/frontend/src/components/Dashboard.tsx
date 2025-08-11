import React, { useState, useEffect, useRef } from 'react'
import StatsCards from './StatsCards'
import VehicleHistory from './VehicleHistory'
import SearchFilters from './SearchFilters'
import LiveSessions from './LiveSessions'
import apiService from '../services/apiService'
import type { GroupedSession, DashboardStats } from '../types/types'
import type { SessionResponse } from '../services/apiService'
import '../styles/dashboard.css'

const REFRESH_INTERVAL = 3000 // 3 seconds

const Dashboard: React.FC = () => {
  const [groupedSessions, setGroupedSessions] = useState<GroupedSession[]>([])
  const [filteredSessions, setFilteredSessions] = useState<GroupedSession[]>([])
  const [stats, setStats] = useState<DashboardStats>({
    current_vehicles: 0,
    total_entries: 0,
    available_slots: 0,
    total_slots: 10
  })

  const [initialLoading, setInitialLoading] = useState(true)
  const loadingRef = useRef(false)
  const [error, setError] = useState<string | null>(null)
  const [isAutoRefreshing, setIsAutoRefreshing] = useState(true)

  // Centralized function to load all dashboard data
  const loadDashboardData = async (mode: 'initial' | 'refresh' = 'refresh') => {
    if (loadingRef.current) return // prevent overlap
    loadingRef.current = true
    if (mode === 'initial') {
      setInitialLoading(true)
    }
    setError(null)
    try {
      const [statsData, sessionsData] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getEnhancedGroupedSessions()
      ])
      setStats(statsData)
      setGroupedSessions(sessionsData)
      setFilteredSessions(sessionsData)
    } catch (err) {
      console.error('Error loading dashboard data:', err)
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data')
    } finally {
      if (mode === 'initial') setInitialLoading(false)
      loadingRef.current = false
    }
  }

  // Handle new session detected from LiveSessions component
  const handleNewSession = async (newSession: SessionResponse) => {
    console.log('🔔 New session detected:', newSession)
    // Trigger immediate refresh when new session is detected
    await loadDashboardData()
  }

  // Main useEffect for initial load and auto-refresh
  useEffect(() => {
    loadDashboardData('initial')

    // Set up auto-refresh every 3 seconds for real-time updates
    const refreshInterval = setInterval(() => {
      if (isAutoRefreshing) {
        loadDashboardData('refresh')
      }
    }, REFRESH_INTERVAL) // Refresh every 3 seconds

    // Cleanup interval on unmount
    return () => {
      clearInterval(refreshInterval)
    }
  }, [isAutoRefreshing]) // Re-run if auto-refresh setting changes

  const handleSearch = async (searchParams: {
    licensePlate?: string
    dateFrom?: Date
    dateTo?: Date
  }) => {
    try {
      console.log('Search params:', searchParams);
      let filtered = [...groupedSessions]; // Create a copy

      // Filter by license plate (case-insensitive)
      if (searchParams.licensePlate && searchParams.licensePlate.trim()) {
        const searchPlate = searchParams.licensePlate.trim().toLowerCase();
        filtered = filtered.filter(session => {
          const sessionPlate = session.licensePlate?.toLowerCase() || '';
          return sessionPlate.includes(searchPlate);
        });
        console.log(`Filtered by plate "${searchParams.licensePlate}": ${filtered.length} results`);
      }

      // Filter by date range
      if (searchParams.dateFrom) {
        const fromDate = new Date(searchParams.dateFrom);
        fromDate.setHours(0, 0, 0, 0); // Start of day

        filtered = filtered.filter(session => {
          // Check both entry and exit times
          const entryDate = session.entryTime ? new Date(session.entryTime) : null;
          const exitDate = session.exitTime ? new Date(session.exitTime) : null;

          return (entryDate && entryDate >= fromDate) ||
                 (exitDate && exitDate >= fromDate);
        });
        console.log(`Filtered by dateFrom ${searchParams.dateFrom}: ${filtered.length} results`);
      }

      if (searchParams.dateTo) {
        const toDate = new Date(searchParams.dateTo);
        toDate.setHours(23, 59, 59, 999); // End of day

        filtered = filtered.filter(session => {
          // Check both entry and exit times
          const entryDate = session.entryTime ? new Date(session.entryTime) : null;
          const exitDate = session.exitTime ? new Date(session.exitTime) : null;

          return (entryDate && entryDate <= toDate) ||
                 (exitDate && exitDate <= toDate);
        });
        console.log(`Filtered by dateTo ${searchParams.dateTo}: ${filtered.length} results`);
      }

      console.log(`Final search result: ${filtered.length} sessions`);
      setFilteredSessions(filtered);
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search. Please try again.');
    }
  }

  const clearFilters = () => {
    setFilteredSessions(groupedSessions)
  }

  return (
    <div className="dashboard">
      <div className="dashboard-content">
        <div className="dashboard-header">
          <h1>Smart Parking Dashboard</h1>
          <div className="real-time-indicator">
            <div className={`status-dot ${isAutoRefreshing ? 'active' : 'inactive'}`}></div>
            <span className="status-text">
              {isAutoRefreshing ? 'Live Updates' : 'Updates Paused'}
            </span>
            <button
              className="toggle-refresh"
              onClick={() => setIsAutoRefreshing(!isAutoRefreshing)}
              title={isAutoRefreshing ? 'Pause auto-refresh' : 'Resume auto-refresh'}
            >
              {isAutoRefreshing ? '⏸️' : '▶️'}
            </button>
            <button
              className="toggle-refresh"
              onClick={() => loadDashboardData('refresh')}
              title="Manual refresh"
            >
              🔄
            </button>
          </div>
        </div>
        {initialLoading && (
          <div className="loading-state">
            <p>Loading dashboard data...</p>
          </div>
        )}
        {error && !initialLoading && (
          <div className="error-state">
            <p style={{ color: 'red' }}>{error}</p>
            <button onClick={() => loadDashboardData('initial')}>Retry</button>
          </div>
        )}
        {!initialLoading && !error && (
          <>
            <StatsCards stats={stats} />
            <div className="dashboard-main">
              <div className="dashboard-left">
                <SearchFilters onSearch={handleSearch} onClear={clearFilters} />
                <VehicleHistory sessions={filteredSessions} onRefresh={() => loadDashboardData('refresh')} />
              </div>
              <div className="dashboard-right">
                <LiveSessions onNewSession={handleNewSession} />
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default Dashboard
