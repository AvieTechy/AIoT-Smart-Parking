import React from 'react'
import { format } from 'date-fns'
import { Car, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import type { GroupedSession } from '../types/types'
import '../styles/vehicle-history.css'

interface VehicleHistoryProps {
  sessions: GroupedSession[]
}

const VehicleHistory: React.FC<VehicleHistoryProps> = ({ sessions }) => {
  if (sessions.length === 0) {
    return (
      <div className="no-data">
        <Car size={48} />
        <p>No sessions found matching your criteria.</p>
      </div>
    )
  }

  return (
    <div className="vehicle-history">
      <div className="history-header">
        <h3>Parking Sessions</h3>
        <span className="record-count">{sessions.length} sessions</span>
      </div>
      
      <div className="history-table-container">
        <table className="history-table">
          <thead>
            <tr>
              <th>Face ID</th>
              <th>License Plate</th>
              <th>Entry Time</th>
              <th>Exit Time</th>
              <th>Status</th>
              <th>Entry Images</th>
              <th>Exit Images</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session, index) => {
              const isActive = session.status === 'active'
              return (
                <tr key={`${session.faceId}-${index}`}>
                  <td>
                    <div className="face-id">
                      {session.faceUrl ? (
                        <img 
                          src={session.faceUrl} 
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
                      <span>{session.faceId}</span>
                    </div>
                  </td>
                  <td className="license-plate">
                    {session.licensePlate !== 'N/A' ? session.licensePlate : (
                      <span className="detecting">Detecting...</span>
                    )}
                  </td>
                  <td>
                    {session.entryTime ? (
                      <div className="time-info">
                        <Clock size={14} />
                        <span>{format(session.entryTime, 'HH:mm:ss dd/MM/yyyy')}</span>
                      </div>
                    ) : (
                      <span className="no-time">-</span>
                    )}
                  </td>
                  <td>
                    {session.exitTime ? (
                      <div className="time-info">
                        <Clock size={14} />
                        <span>{format(session.exitTime, 'HH:mm:ss dd/MM/yyyy')}</span>
                      </div>
                    ) : (
                      <span className="no-time">-</span>
                    )}
                  </td>
                  <td>
                    <div className={`status-badge ${isActive ? 'active' : 'completed'}`}>
                      {isActive ? (
                        <AlertCircle size={14} />
                      ) : (
                        <CheckCircle size={14} />
                      )}
                      <span>{isActive ? 'Parked' : 'Completed'}</span>
                    </div>
                  </td>
                  <td>
                    <div className="image-links">
                      {session.faceUrl && (
                        <a href={session.faceUrl} target="_blank" rel="noopener noreferrer" className="image-link">
                          👤 Face
                        </a>
                      )}
                      {session.plateUrl && (
                        <a href={session.plateUrl} target="_blank" rel="noopener noreferrer" className="image-link">
                          📋 Plate
                        </a>
                      )}
                      {!session.faceUrl && !session.plateUrl && (
                        <span className="no-images">No images</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="image-links">
                      {session.exitFaceUrl && (
                        <a href={session.exitFaceUrl} target="_blank" rel="noopener noreferrer" className="image-link">
                          👤 Face
                        </a>
                      )}
                      {session.exitPlateUrl && (
                        <a href={session.exitPlateUrl} target="_blank" rel="noopener noreferrer" className="image-link">
                          📋 Plate
                        </a>
                      )}
                      {session.exitTime && session.exitSessionId && !(session.exitFaceUrl || session.exitPlateUrl) && (
                        <div className="placeholder-images">
                          <span className="image-link placeholder">👤 Face (Available)</span>
                          <span className="image-link placeholder">📋 Plate (Available)</span>
                        </div>
                      )}
                      {!session.exitTime && (
                        <span className="no-images">Not exited</span>
                      )}
                      {session.exitTime && !session.exitSessionId && !(session.exitFaceUrl || session.exitPlateUrl) && (
                        <span className="no-images">No images</span>
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
