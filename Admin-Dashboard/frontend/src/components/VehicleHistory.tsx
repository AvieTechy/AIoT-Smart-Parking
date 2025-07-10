import React from 'react'
import { format } from 'date-fns'
import { Car, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import type { Vehicle } from '../types/types'
import '../styles/vehicle-history.css'

interface VehicleHistoryProps {
  vehicles: Vehicle[]
}

const VehicleHistory: React.FC<VehicleHistoryProps> = ({ vehicles }) => {
  if (vehicles.length === 0) {
    return (
      <div className="no-data">
        <Car size={48} />
        <p>No vehicles found matching your criteria.</p>
      </div>
    )
  }

  return (
    <div className="vehicle-history">
      <div className="history-header">
        <h3>Session History (Entry/Exit)</h3>
        <span className="record-count">{vehicles.length} records</span>
      </div>
      
      <div className="history-table-container">
        <table className="history-table">
          <thead>
            <tr>
              <th>Session ID</th>
              <th>License Plate</th>
              <th>Face ID</th>
              <th>Gate</th>
              <th>Timestamp</th>
              <th>Status</th>
              <th>Images</th>
            </tr>
          </thead>
          <tbody>
            {vehicles.map((vehicle) => {
              return (
                <tr key={vehicle.id}>
                  <td>{vehicle.id.slice(0, 8)}...</td>
                  <td className="license-plate">
                    {vehicle.licensePlate !== 'Detecting...' ? vehicle.licensePlate : (
                      <span className="detecting">Detecting...</span>
                    )}
                  </td>
                  <td>
                    <div className="face-id">
                      {vehicle.faceUrl ? (
                        <img 
                          src={vehicle.faceUrl} 
                          alt="Face"
                          className="face-thumbnail"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement
                            target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yMCAyNUMxNi42ODYzIDI1IDE0IDIyLjMxMzcgMTQgMTlDMTQgMTUuNjg2MyAxNi42ODYzIDEzIDIwIDEzQzIzLjMxMzcgMTMgMjYgMTUuNjg2MyAyNiAxOUMyNiAyMi4zMTM3IDIzLjMxMzcgMjUgMjAgMjVaIiBmaWxsPSIjOUNBM0FGIi8+CjxwYXRoIGQ9Ik0yOCAzMEMyOCAyNi42ODYzIDI0LjQxODMgMjQgMjAgMjRDMTUuNTgxNyAyNCAxMiAyNi42ODYzIDEyIDMwVjMySDI4VjMwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K'
                          }}
                        />
                      ) : (
                        <div className="no-image">No Image</div>
                      )}
                      <span>{vehicle.faceId}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`gate-badge ${vehicle.gate?.toLowerCase()}`}>
                      {vehicle.gate || 'Unknown'}
                    </span>
                  </td>
                  <td>
                    <div className="time-info">
                      <Clock size={14} />
                      <span>{format(vehicle.entryTime, 'HH:mm:ss dd/MM/yyyy')}</span>
                    </div>
                  </td>
                  <td>
                    <div className={`status-badge ${vehicle.status}`}>
                      {vehicle.status === 'parked' ? (
                        <AlertCircle size={14} />
                      ) : (
                        <CheckCircle size={14} />
                      )}
                      <span>{vehicle.status === 'parked' ? 'Active' : 'Completed'}</span>
                    </div>
                  </td>
                  <td>
                    <div className="image-links">
                      {vehicle.plateUrl && (
                        <a href={vehicle.plateUrl} target="_blank" rel="noopener noreferrer" className="image-link">
                          📋 Plate
                        </a>
                      )}
                      {vehicle.faceUrl && (
                        <a href={vehicle.faceUrl} target="_blank" rel="noopener noreferrer" className="image-link">
                          👤 Face
                        </a>
                      )}
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default VehicleHistory
