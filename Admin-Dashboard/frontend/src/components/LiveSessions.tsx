import React, { useState, useEffect } from 'react';
import { Clock, Car, ArrowRight, ArrowLeft, Wifi, WifiOff } from 'lucide-react';
import apiService from '../services/apiService';
import type { SessionResponse } from '../services/apiService';
import '../styles/live-sessions.css';

interface LiveSessionsProps {
  onNewSession?: (session: SessionResponse) => void;
}

const LiveSessions: React.FC<LiveSessionsProps> = ({ onNewSession }) => {
  const [latestSessions, setLatestSessions] = useState<SessionResponse[]>([]);
  const [isConnected, setIsConnected] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Polling function to check for new sessions
  const checkForNewSessions = async () => {
    try {
      setIsConnected(true);

      // Get recent sessions (last 10)
      const recentSessions = await apiService.getSessions(undefined, 10);

      // Sort by timestamp (newest first)
      const sortedSessions = recentSessions.sort((a, b) =>
        new Date(b.session.timestamp).getTime() - new Date(a.session.timestamp).getTime()
      );

      // Check if we have new sessions
      if (latestSessions.length > 0 && sortedSessions.length > 0) {
        const latestTimestamp = new Date(latestSessions[0]?.session.timestamp || 0);
        const newSessions = sortedSessions.filter(session =>
          new Date(session.session.timestamp) > latestTimestamp
        );

        // Notify parent component about new sessions
        if (newSessions.length > 0 && onNewSession) {
          newSessions.forEach(session => onNewSession(session));
        }
      }

      setLatestSessions(sortedSessions.slice(0, 5)); // Keep only 5 latest
      setLastUpdate(new Date());

    } catch (error) {
      console.error('Error checking for new sessions:', error);
      setIsConnected(false);
    }
  };

  // Start polling when component mounts
  useEffect(() => {
    // Initial load
    checkForNewSessions();

    // Set up polling every 5 seconds
    const interval = setInterval(() => {
      checkForNewSessions();
    }, 5000);

    // Cleanup on unmount
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, []); // Empty dependency array for initial setup

  // Update polling when latestSessions changes (for new session detection)
  useEffect(() => {
    // This effect runs when latestSessions changes, but we don't want to restart polling
    // Just for new session detection logic
  }, [latestSessions]);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getGateIcon = (gate: 'In' | 'Out') => {
    return gate === 'In' ? <ArrowRight size={16} /> : <ArrowLeft size={16} />;
  };

  const getGateColor = (gate: 'In' | 'Out') => {
    return gate === 'In' ? 'gate-in' : 'gate-out';
  };

  return (
    <div className="live-sessions">
      <div className="live-sessions-header">
        <div className="header-left">
          <Clock size={20} />
          <h3>Live Sessions</h3>
        </div>
        <div className="connection-status">
          {isConnected ? (
            <div className="connected">
              <Wifi size={16} />
              <span>Connected</span>
            </div>
          ) : (
            <div className="disconnected">
              <WifiOff size={16} />
              <span>Disconnected</span>
            </div>
          )}
          <small>Last update: {formatTimestamp(lastUpdate.toISOString())}</small>
        </div>
      </div>

      <div className="sessions-list">
        {latestSessions.length === 0 ? (
          <div className="no-sessions">
            <Car size={24} />
            <p>No recent sessions</p>
          </div>
        ) : (
          latestSessions.map((sessionResponse, index) => (
            <div key={sessionResponse.session_id} className={`session-item ${index === 0 ? 'latest' : ''}`}>
              <div className="session-info">
                <div className="session-header">
                  <div className={`gate-badge ${getGateColor(sessionResponse.session.gate)}`}>
                    {getGateIcon(sessionResponse.session.gate)}
                    <span>{sessionResponse.session.gate}</span>
                  </div>
                  <span className="session-time">
                    {formatTimestamp(sessionResponse.session.timestamp)}
                  </span>
                </div>

                <div className="session-details">
                  <div className="session-field">
                    <strong>Plate:</strong>
                    <span>{sessionResponse.session.plateNumber || 'Detecting...'}</span>
                  </div>
                  
                </div>

                <div className="session-images">
                  {sessionResponse.session.plateUrl && (
                    <img
                      src={sessionResponse.session.plateUrl}
                      alt="License plate"
                      className="session-image plate-image"
                    />
                  )}
                  {sessionResponse.session.faceUrl && (
                    <img
                      src={sessionResponse.session.faceUrl}
                      alt="Face"
                      className="session-image face-image"
                    />
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="auto-refresh-info">
        <div className="refresh-indicator">
          <div className="pulse-dot"></div>
          <span>Auto-refreshing every 5 seconds</span>
        </div>
      </div>
    </div>
  );
};

export default LiveSessions;
