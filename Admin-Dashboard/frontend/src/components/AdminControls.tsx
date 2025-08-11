import React, { useState } from 'react';
import { Settings, Save, AlertCircle } from 'lucide-react';
import apiService from '../services/apiService';
import type { DashboardStats } from '../types/types';
import '../styles/admin-controls.css';

interface AdminControlsProps {
  currentStats: DashboardStats;
  onStatsUpdate: (newStats: DashboardStats) => void;
}

const AdminControls: React.FC<AdminControlsProps> = ({ currentStats, onStatsUpdate }) => {
  const [totalSlots, setTotalSlots] = useState(currentStats.total_slots || 10);
  const [isUpdating, setIsUpdating] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleUpdateTotalSlots = async () => {
    if (totalSlots < 0) {
      setMessage({ type: 'error', text: 'Total slots cannot be negative' });
      return;
    }

    if (totalSlots < currentStats.current_vehicles) {
      setMessage({
        type: 'error',
        text: `Total slots cannot be less than current vehicles (${currentStats.current_vehicles})`
      });
      return;
    }

    setIsUpdating(true);
    setMessage(null);

    try {
      const result = await apiService.updateTotalSlots(totalSlots);
      if (result.success) {
        onStatsUpdate(result.updated_stats);
        setMessage({ type: 'success', text: `Successfully updated total slots to ${totalSlots}` });

        // Clear success message after 3 seconds
        setTimeout(() => setMessage(null), 3000);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update total slots';
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setIsUpdating(false);
    }
  };

  const handleInputChange = (value: string) => {
    const numValue = parseInt(value) || 0;
    setTotalSlots(numValue);
    setMessage(null); // Clear any existing messages when user types
  };

  return (
    <div className="admin-controls">
      <div className="admin-controls-header">
        <Settings size={20} />
        <h3>Admin Controls</h3>
      </div>

      <div className="control-section">
        <div className="control-item">
          <label htmlFor="total-slots-input">Total Parking Slots</label>
          <div className="input-group">
            <input
              id="total-slots-input"
              type="number"
              value={totalSlots}
              onChange={(e) => handleInputChange(e.target.value)}
              min="0"
              className="control-input"
              disabled={isUpdating}
              placeholder="Enter total slots"
            />
            <button
              onClick={handleUpdateTotalSlots}
              disabled={isUpdating || totalSlots === currentStats.total_slots}
              className="update-button"
            >
              <Save size={16} />
              {isUpdating ? 'Updating...' : 'Update'}
            </button>
          </div>
          <small className="input-help">
            Current: {currentStats.total_slots} slots |
            Available: {currentStats.available_slots} |
            Occupied: {currentStats.current_vehicles}
          </small>
        </div>

        {message && (
          <div className={`message ${message.type}`}>
            <AlertCircle size={16} />
            <span>{message.text}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminControls;
