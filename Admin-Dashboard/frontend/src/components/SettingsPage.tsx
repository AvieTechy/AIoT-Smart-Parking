import React, { useState, useEffect } from 'react';
import { Settings, Database, Wifi, AlertCircle } from 'lucide-react';
import AdminControls from './AdminControls';
import apiService from '../services/apiService';
import type { DashboardStats } from '../types/types';
import '../styles/settings-page.css';

const SettingsPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    current_vehicles: 0,
    total_entries: 0,
    available_slots: 0,
    total_slots: 10
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load current stats when page loads
  useEffect(() => {
    const loadStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const dashboardStats = await apiService.getDashboardStats();
        setStats(dashboardStats);
      } catch (err) {
        console.error('Error loading stats:', err);
        setError('Failed to load current statistics');
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, []);

  const handleStatsUpdate = (newStats: DashboardStats) => {
    setStats(newStats);
  };

  return (
    <div className="settings-page">
      <div className="settings-header">
        <div className="header-content">
          <div className="header-title">
            <Settings size={32} />
            <div>
              <h1>System Settings</h1>
              <p>Configure parking system parameters and view system status</p>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-content">
        {loading && (
          <div className="loading-state">
            <p>Loading settings...</p>
          </div>
        )}

        {error && (
          <div className="error-state">
            <AlertCircle size={20} />
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>Retry</button>
          </div>
        )}

        {!loading && !error && (
          <>
            {/* Current System Status */}
            <div className="settings-section">
              <div className="section-header">
                <Database size={20} />
                <h2>System Status</h2>
              </div>
              <div className="status-grid">
                <div className="status-item">
                  <span className="status-label">Current Vehicles:</span>
                  <span className="status-value">{stats.current_vehicles}</span>
                </div>
                <div className="status-item">
                  <span className="status-label">Total Entries:</span>
                  <span className="status-value">{stats.total_entries}</span>
                </div>
                <div className="status-item">
                  <span className="status-label">Available Slots:</span>
                  <span className="status-value">{stats.available_slots}</span>
                </div>
                <div className="status-item">
                  <span className="status-label">Total Slots:</span>
                  <span className="status-value">{stats.total_slots}</span>
                </div>
              </div>
            </div>

            {/* Admin Controls */}
            <div className="settings-section">
              <div className="section-header">
                <Wifi size={20} />
                <h2>Parking Configuration</h2>
              </div>
              <AdminControls currentStats={stats} onStatsUpdate={handleStatsUpdate} />
            </div>

            {/* Additional Settings */}
            <div className="settings-section">
              <div className="section-header">
                <Settings size={20} />
                <h2>Additional Settings</h2>
              </div>
              <div className="additional-settings">
                <div className="setting-item">
                  <h3>System Information</h3>
                  <div className="setting-details">
                    <p><strong>Backend:</strong> FastAPI + Firebase</p>
                    <p><strong>Frontend:</strong> React + TypeScript</p>
                    <p><strong>Database:</strong> Firestore</p>
                    <p><strong>AI Services:</strong> Face Recognition, License Plate OCR</p>
                  </div>
                </div>

                <div className="setting-item">
                  <h3>API Endpoints</h3>
                  <div className="setting-details">
                    <p><strong>Dashboard Stats:</strong> /api/dashboard/stats</p>
                    <p><strong>Sessions:</strong> /api/sessions</p>
                    <p><strong>Parking Slots:</strong> /api/parking/slots</p>
                    <p><strong>API Documentation:</strong> <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">http://localhost:8000/docs</a></p>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default SettingsPage;
