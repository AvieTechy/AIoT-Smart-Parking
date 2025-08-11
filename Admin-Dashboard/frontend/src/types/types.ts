// Legacy Vehicle interface (for backward compatibility)
export interface Vehicle {
  id: string
  licensePlate: string
  faceId: string
  entryTime: Date
  exitTime: Date | null
  status: 'parked' | 'exited'
  plateUrl?: string
  faceUrl?: string
  gate?: string
}

// Backend model interfaces
export interface Session {
  plateUrl: string
  faceUrl: string
  timestamp: string
  gate: 'In' | 'Out'
  isOut: boolean
  faceIndex: string
  plateNumber?: string
}

export interface SessionResponse {
  session_id: string
  session: Session
}

export interface IsNewSession {
  status: boolean
  sessionID: string
}

export interface MatchingVerify {
  sessionID: string
  isMatch: boolean
}

export interface SessionMap {
  entrySessionID: string
  exitSessionID: string
}

export interface ParkingSlot {
  location_code: string
  is_occupied: boolean
  updated_at: string
}

export interface ParkingSlotResponse {
  slot_id: string
  slot: ParkingSlot
}

export interface DashboardStats {
  current_vehicles: number;
  total_entries: number;
  available_slots: number;
  total_slots?: number;
}

export interface StatsPeriod {
  period: 'hour' | 'day' | 'week' | 'month' | 'year'
  entries: number
  exits: number
  date: string
}

export interface SearchFilters {
  licensePlate?: string
  dateFrom?: Date
  dateTo?: Date
  gate?: 'In' | 'Out'
  status?: 'parked' | 'exited'
}

// Grouped session interface
export interface GroupedSession {
  faceId: string
  licensePlate: string
  entryTime: Date | null
  exitTime: Date | null
  status: 'active' | 'completed' | 'failed' | 'unverified'
  entrySessionId?: string
  exitSessionId?: string
  // Entry session images
  faceUrl?: string
  plateUrl?: string
  // Exit session images
  exitFaceUrl?: string
  exitPlateUrl?: string
  entryGate?: string
  exitGate?: string
  // Parking duration in minutes
  duration?: number
  // Face matching verification (new fields)
  faceMatchVerified?: boolean
  faceMatchResult?: boolean
}
