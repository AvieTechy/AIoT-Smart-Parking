import React, { useState, useEffect } from 'react'
import { MdRefresh, MdDirectionsCar, MdCheckBoxOutlineBlank, MdInfo } from 'react-icons/md'
import { FaCar, FaSquare } from 'react-icons/fa'
import apiService from '../services/apiService'
import cacheService from '../services/cacheService'
import { useParking } from '../contexts/ParkingContext'
import '../styles/parking-map.css'

interface ParkingSlot {
  slot_id: string
  location_code: string
  is_occupied: boolean
  updated_at: string
}

interface ParkingStats {
  total_slots: number
  occupied_slots: number
  available_slots: number
  occupancy_rate: number
  current_vehicles: number
}

const ParkingMap: React.FC = () => {
  // Use global parking context instead of local state
  const { 
    state: { slots, stats, loading, error }, 
    updateSlot, 
    revertSlot, 
    setSlots, 
    setStats, 
    setLoading, 
    setError 
  } = useParking();
  
  const [selectedSlot, setSelectedSlot] = useState<ParkingSlot | null>(null)

  useEffect(() => {
    loadParkingData()
    
    // Auto-refresh every 60 seconds (reduced from 30)
    const interval = setInterval(loadParkingData, 60000)
    return () => clearInterval(interval)
  }, [])

  const loadParkingData = async () => {
    const startTime = performance.now();
    
    try {
      setError(null)
      
      console.log('🔄 Starting to load parking data...');
      
      // Load stats first as it's usually faster
      const statsStart = performance.now();
      const statsPromise = apiService.getParkingStats();
      const slotsPromise = apiService.getParkingSlots();
      
      // Set stats immediately when available
      try {
        const statsData = await statsPromise;
        const statsEnd = performance.now();
        console.log(`📊 Stats loaded in ${(statsEnd - statsStart).toFixed(2)}ms`);
        setStats(statsData);
        setLoading(false); // Hide main loading after stats
      } catch (err) {
        console.warn('Failed to load stats:', err);
      }
      
      // Then load slots
      try {
        const slotsStart = performance.now();
        const slotsData = await slotsPromise;
        const slotsEnd = performance.now();
        console.log(`🅿️ Slots loaded in ${(slotsEnd - slotsStart).toFixed(2)}ms`);
        setSlots(slotsData);
      } catch (err) {
        console.error('Failed to load slots:', err);
        setError('Failed to load parking slots');
      }
      
    } catch (err) {
      console.error('Error loading parking data:', err)
      setError('Failed to load parking data')
      setLoading(false);
    } finally {
      const endTime = performance.now();
      console.log(`✅ Total parking data load time: ${(endTime - startTime).toFixed(2)}ms`);
    }
  }

  const handleSlotClick = (slot: ParkingSlot) => {
    setSelectedSlot(slot)
  }

  const handleSlotToggle = async (slotId: string, newStatus: boolean) => {
    // Optimistic update using context
    updateSlot(slotId, newStatus);

    try {
      // Send API request
      await apiService.updateSlotOccupancy(slotId, newStatus);
      
      // Clear cache to ensure fresh data on next request
      cacheService.delete('parking_slots');
      cacheService.delete('parking_stats');
      cacheService.delete('available_slots');
      
      console.log(`✅ Slot ${slotId} updated successfully to ${newStatus ? 'occupied' : 'available'}`);
      
    } catch (err) {
      console.error('Error updating slot:', err);
      
      // Revert optimistic update on error
      revertSlot(slotId, newStatus);
      
      alert('Failed to update slot status. Please try again.');
    } finally {
      setSelectedSlot(null);
    }
  }

  const groupSlotsByRow = () => {
    const grouped: { [key: string]: ParkingSlot[] } = {}
    
    slots.forEach(slot => {
      const row = slot.location_code.charAt(0)
      if (!grouped[row]) {
        grouped[row] = []
      }
      grouped[row].push(slot)
    })

    // Sort slots within each row
    Object.keys(grouped).forEach(row => {
      grouped[row].sort((a, b) => {
        const numA = parseInt(a.location_code.substring(1))
        const numB = parseInt(b.location_code.substring(1))
        return numA - numB
      })
    })

    return grouped
  }

  if (loading) {
    return (
      <div className="parking-map">
        <div className="parking-map-header">
          <h1>Parking Map</h1>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading parking map...</p>
        </div>
        
        {/* Show partial data if available */}
        {stats && (
          <div className="parking-overview">
            <div className="overview-card">
              <span className="overview-label">Total Slots:</span>
              <span className="overview-value">{stats.total_slots}</span>
            </div>
            <div className="overview-card">
              <span className="overview-label">Available:</span>
              <span className="overview-value available">{stats.available_slots}</span>
            </div>
            <div className="overview-card">
              <span className="overview-label">Occupied:</span>
              <span className="overview-value occupied">{stats.occupied_slots}</span>
            </div>
            <div className="overview-card">
              <span className="overview-label">Occupancy Rate:</span>
              <span className="overview-value">{stats.occupancy_rate}%</span>
            </div>
          </div>
        )}
      </div>
    )
  }

  if (error) {
    return (
      <div className="parking-map">
        <div className="error-state">
          <p style={{ color: 'red' }}>{error}</p>
          <button onClick={loadParkingData}>Retry</button>
        </div>
      </div>
    )
  }

  const groupedSlots = groupSlotsByRow()

  return (
    <div className="parking-map">
      <div className="parking-map-header">
        <h1>Parking Map</h1>
        <div className="parking-controls">
          <button onClick={loadParkingData} className="refresh-button">
            <MdRefresh size={16} />
            Refresh
          </button>
        </div>
      </div>

      {stats && (
        <div className="parking-overview">
          <div className="overview-card">
            <span className="overview-label">Total Slots:</span>
            <span className="overview-value">{stats.total_slots}</span>
          </div>
          <div className="overview-card">
            <span className="overview-label">Available:</span>
            <span className="overview-value available">{stats.available_slots}</span>
          </div>
          <div className="overview-card">
            <span className="overview-label">Occupied:</span>
            <span className="overview-value occupied">{stats.occupied_slots}</span>
          </div>
          <div className="overview-card">
            <span className="overview-label">Occupancy Rate:</span>
            <span className="overview-value">{stats.occupancy_rate}%</span>
          </div>
        </div>
      )}

      <div className="parking-legend">
        <div className="legend-item">
          <div className="legend-color available"></div>
          <span>Available</span>
        </div>
        <div className="legend-item">
          <div className="legend-color occupied"></div>
          <span>Occupied</span>
        </div>
      </div>

      <div className="parking-grid">
        {loading ? (
          <div className="slots-loading">
            <div className="loading-spinner small"></div>
            <p>Loading parking slots...</p>
          </div>
        ) : (
          Object.keys(groupedSlots).sort().map(row => (
            <div key={row} className="parking-row">
              <div className="row-label">Row {row}</div>
              <div className="slots-container">
                {groupedSlots[row].map(slot => (
                  <div
                    key={slot.slot_id}
                    className={`parking-slot ${slot.is_occupied ? 'occupied' : 'available'}`}
                    onClick={() => handleSlotClick(slot)}
                    title={`${slot.location_code} - ${slot.is_occupied ? 'Occupied' : 'Available'}`}
                  >
                    <div className="slot-code">{slot.location_code}</div>
                    <div className="slot-status">
                      {slot.is_occupied ? <FaCar size={16} /> : <FaSquare size={16} />}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {selectedSlot && (
        <div className="slot-modal-overlay" onClick={() => setSelectedSlot(null)}>
          <div className="slot-modal" onClick={e => e.stopPropagation()}>
            <h3>Slot {selectedSlot.location_code}</h3>
            <div className="slot-details">
              <p><strong>Status:</strong> {selectedSlot.is_occupied ? 'Occupied' : 'Available'}</p>
              <p><strong>Last Updated:</strong> {new Date(selectedSlot.updated_at).toLocaleString()}</p>
            </div>
            <div className="slot-actions">
              <button
                onClick={() => handleSlotToggle(selectedSlot.slot_id, !selectedSlot.is_occupied)}
                className={`toggle-button ${selectedSlot.is_occupied ? 'free' : 'occupy'}`}
              >
                Mark as {selectedSlot.is_occupied ? 'Available' : 'Occupied'}
              </button>
              <button onClick={() => setSelectedSlot(null)} className="cancel-button">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ParkingMap
