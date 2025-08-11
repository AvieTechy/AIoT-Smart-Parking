import React from 'react'
import { format } from 'date-fns'
import { Car, Clock, CheckCircle, AlertCircle, RefreshCcw } from 'lucide-react'
import type { GroupedSession } from '../types/types'
import '../styles/vehicle-history.css'
import apiService from '../services/apiService'

interface VehicleHistoryProps {
  sessions: GroupedSession[]
  onRefresh?: () => void | Promise<void>
}

const VehicleHistory: React.FC<VehicleHistoryProps> = ({ sessions, onRefresh }) => {
  const handleFinalize = async (exitSessionId?: string) => {
    if (!exitSessionId) return
    try {
      if (!confirm('Finalize this exit (requires successful verification)?')) return
      const res = await apiService.finalizeExitSession(exitSessionId)
      console.log('Finalize result:', res)
      if (onRefresh) await onRefresh()
    } catch (e:any) {
      alert(e.message || 'Finalize failed')
    }
  }

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
        {onRefresh && (
          <button className="refresh-button" onClick={()=>onRefresh()} title="Refresh list">
            <RefreshCcw size={16} />
          </button>
        )}
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
              <th>Exit Images / Actions</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session, index) => {
              const hasEntry = !!session.entryTime
              const hasExit = !!session.exitTime
              const showFinalize = session.exitSessionId && session.status === 'unverified'

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
                    {hasEntry ? (
                      <div className="time-info">
                        <Clock size={14} />
                        <span>{format(session.entryTime!, 'HH:mm:ss dd/MM/yyyy')}</span>
                      </div>
                    ) : (
                      <span className="no-time">No entry record</span>
                    )}
                  </td>
                  <td>
                    {hasExit ? (
                      <div className="time-info">
                        <Clock size={14} />
                        <span>{format(session.exitTime!, 'HH:mm:ss dd/MM/yyyy')}</span>
                      </div>
                    ) : (
                      <span className="no-time">Still parking</span>
                    )}
                  </td>
                  <td>
                    <div className={`status-badge ${
                      session.status === 'failed' ? 'failed' :
                      session.status === 'active' ? 'active' :
                      session.status === 'unverified' ? 'unverified' :
                      'completed'
                    }`}>
                      {session.status === 'failed' ? (
                        <AlertCircle size={14} />
                      ) : session.status === 'active' ? (
                        <AlertCircle size={14} />
                      ) : (
                        <CheckCircle size={14} />
                      )}
                      <span>
                        {session.status === 'failed' ? 'Failed' :
                         session.status === 'active' ? 'Parking' :
                         session.status === 'unverified' ? 'Unverified' :
                         'Completed'}
                      </span>
                      {session.faceMatchVerified && (
                        <span className={`verification-badge ${session.faceMatchResult ? 'verified' : 'not-verified'}`}>
                          {session.faceMatchResult ? '✓' : '✗'}
                        </span>
                      )}
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
                      {showFinalize && (
                        <button className="finalize-btn" onClick={() => handleFinalize(session.exitSessionId)}>Finalize</button>
                      )}
                      {session.exitTime && session.exitSessionId && !(session.exitFaceUrl || session.exitPlateUrl) && !showFinalize && (
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
