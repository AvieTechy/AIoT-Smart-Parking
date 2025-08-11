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
  const [isAutoRefreshing, setIsAutoRefreshing] = useState(true)

  // Centralized function to load vehicle history data
    const loadVehicleData = async () => {
      try {
        setLoading(true);
        setError(null);

        console.log('Loading vehicle data with enhanced API...');
        const data = await apiService.getEnhancedGroupedSessions(); // Use enhanced API
        console.log('Loaded', data.length, 'enhanced sessions');

        setGroupedSessions(data);
        setFilteredSessions(data);

      } catch (err) {
        console.error('Error loading vehicle data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load vehicle data');
      } finally {
        setLoading(false);
      }
    };  useEffect(() => {
    // Initial load
    loadVehicleData()

    // Set up auto-refresh every 5 seconds for real-time updates
    const refreshInterval = setInterval(() => {
      if (isAutoRefreshing) {
        console.log('⏰ Auto-refreshing vehicle history data...')
        loadVehicleData()
      }
    }, 5000) // Refresh every 5 seconds

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
      console.log('VehicleHistoryPage - Search params:', searchParams);
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

      console.log(`VehicleHistoryPage - Final search result: ${filtered.length} sessions`);
      setFilteredSessions(filtered);
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search. Please try again.');
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
        <div className="dashboard-header">
          <h1>Vehicle History</h1>

          {/* Real-time indicator */}
          <div className="real-time-indicator">
            <div className={`status-dot ${isAutoRefreshing ? 'active' : 'inactive'}`}></div>
            <span className="status-text">
              {isAutoRefreshing ? 'Live Updates' : 'Updates Paused'}
            </span>
            <span className="last-update">
              Last update: {new Date().toLocaleTimeString()}
            </span>
            <button
              className="toggle-refresh"
              onClick={() => setIsAutoRefreshing(!isAutoRefreshing)}
              title={isAutoRefreshing ? 'Pause auto-refresh' : 'Resume auto-refresh'}
            >
              {isAutoRefreshing ? '⏸️' : '▶️'}
            </button>
          </div>
        </div>

        <SearchFilters onSearch={handleSearch} onClear={clearFilters} />
        <VehicleHistory sessions={filteredSessions} onRefresh={loadVehicleData} />
      </div>
    </div>
  )
}

export default VehicleHistoryPage
