import React, { createContext, useContext, useReducer } from 'react';
import type { ReactNode } from 'react';

// Types
interface ParkingSlot {
  slot_id: string;
  location_code: string;
  is_occupied: boolean;
  updated_at: string;
}

interface ParkingStats {
  total_slots: number;
  occupied_slots: number;
  available_slots: number;
  occupancy_rate: number;
  current_vehicles: number;
}

interface ParkingState {
  slots: ParkingSlot[];
  stats: ParkingStats | null;
  loading: boolean;
  error: string | null;
}

// Action types
type ParkingAction = 
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_SLOTS'; payload: ParkingSlot[] }
  | { type: 'SET_STATS'; payload: ParkingStats }
  | { type: 'UPDATE_SLOT'; payload: { slotId: string; isOccupied: boolean } }
  | { type: 'REVERT_SLOT'; payload: { slotId: string; isOccupied: boolean } };

// Initial state
const initialState: ParkingState = {
  slots: [],
  stats: null,
  loading: true,
  error: null,
};

// Reducer
function parkingReducer(state: ParkingState, action: ParkingAction): ParkingState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
      
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
      
    case 'SET_SLOTS':
      return { ...state, slots: action.payload, loading: false };
      
    case 'SET_STATS':
      return { ...state, stats: action.payload };
      
    case 'UPDATE_SLOT': {
      const { slotId, isOccupied } = action.payload;
      
      // Find the slot being updated
      const currentSlot = state.slots.find(s => s.slot_id === slotId);
      if (!currentSlot) return state;
      
      // Only update if status actually changes
      if (currentSlot.is_occupied === isOccupied) return state;
      
      // Update slots
      const updatedSlots = state.slots.map(slot =>
        slot.slot_id === slotId
          ? { ...slot, is_occupied: isOccupied, updated_at: new Date().toISOString() }
          : slot
      );
      
      // Update stats
      const updatedStats = state.stats ? {
        ...state.stats,
        occupied_slots: isOccupied 
          ? state.stats.occupied_slots + 1 
          : state.stats.occupied_slots - 1,
        available_slots: isOccupied
          ? state.stats.available_slots - 1 
          : state.stats.available_slots + 1,
        occupancy_rate: state.stats.total_slots > 0 
          ? Math.round(((isOccupied ? state.stats.occupied_slots + 1 : state.stats.occupied_slots - 1) / state.stats.total_slots * 100) * 100) / 100
          : 0
      } : null;
      
      return {
        ...state,
        slots: updatedSlots,
        stats: updatedStats
      };
    }
    
    case 'REVERT_SLOT': {
      const { slotId, isOccupied } = action.payload;
      
      // Revert slot status (opposite of what was attempted)
      const revertedSlots = state.slots.map(slot =>
        slot.slot_id === slotId
          ? { ...slot, is_occupied: !isOccupied }
          : slot
      );
      
      // Revert stats
      const revertedStats = state.stats ? {
        ...state.stats,
        occupied_slots: isOccupied 
          ? state.stats.occupied_slots - 1 // Revert increase
          : state.stats.occupied_slots + 1, // Revert decrease
        available_slots: isOccupied
          ? state.stats.available_slots + 1 // Revert decrease
          : state.stats.available_slots - 1, // Revert increase
        occupancy_rate: state.stats.total_slots > 0 
          ? Math.round(((isOccupied ? state.stats.occupied_slots - 1 : state.stats.occupied_slots + 1) / state.stats.total_slots * 100) * 100) / 100
          : 0
      } : null;
      
      return {
        ...state,
        slots: revertedSlots,
        stats: revertedStats
      };
    }
    
    default:
      return state;
  }
}

// Context
interface ParkingContextType {
  state: ParkingState;
  dispatch: React.Dispatch<ParkingAction>;
  // Helper functions
  updateSlot: (slotId: string, isOccupied: boolean) => void;
  revertSlot: (slotId: string, isOccupied: boolean) => void;
  setSlots: (slots: ParkingSlot[]) => void;
  setStats: (stats: ParkingStats) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const ParkingContext = createContext<ParkingContextType | undefined>(undefined);

// Provider component
interface ParkingProviderProps {
  children: ReactNode;
}

export const ParkingProvider: React.FC<ParkingProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(parkingReducer, initialState);

  // Helper functions
  const updateSlot = (slotId: string, isOccupied: boolean) => {
    dispatch({ type: 'UPDATE_SLOT', payload: { slotId, isOccupied } });
  };

  const revertSlot = (slotId: string, isOccupied: boolean) => {
    dispatch({ type: 'REVERT_SLOT', payload: { slotId, isOccupied } });
  };

  const setSlots = (slots: ParkingSlot[]) => {
    dispatch({ type: 'SET_SLOTS', payload: slots });
  };

  const setStats = (stats: ParkingStats) => {
    dispatch({ type: 'SET_STATS', payload: stats });
  };

  const setLoading = (loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  const setError = (error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  return (
    <ParkingContext.Provider 
      value={{ 
        state, 
        dispatch, 
        updateSlot, 
        revertSlot, 
        setSlots, 
        setStats, 
        setLoading, 
        setError 
      }}
    >
      {children}
    </ParkingContext.Provider>
  );
};

// Custom hook
export const useParking = () => {
  const context = useContext(ParkingContext);
  if (context === undefined) {
    throw new Error('useParking must be used within a ParkingProvider');
  }
  return context;
};

export default ParkingContext;
