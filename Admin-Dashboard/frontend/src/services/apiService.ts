const API_BASE_URL = 'http://localhost:8000';

// Session types matching backend models
export interface Session {
  plateUrl: string;
  faceUrl: string;
  timestamp: string;
  gate: 'In' | 'Out';
  isOut: boolean;
  faceIndex: string;
  plateNumber?: string;
}

export interface SessionResponse {
  session_id: string;
  session: Session;
}

export interface IsNewSession {
  status: boolean;
  sessionID: string;
}

export interface MatchingVerify {
  sessionID: string;
  isMatch: boolean;
}

export interface SessionMap {
  entrySessionID: string;
  exitSessionID: string;
}

export interface ParkingSlot {
  location_code: string;
  is_occupied: boolean;
  updated_at: string;
}

export interface ParkingSlotResponse {
  slot_id: string;
  slot: ParkingSlot;
}

export interface DashboardStats {
  currentVehicles: number;
  totalEntries: number;
  totalExits: number;
  occupancyRate: number;
  totalParkedToday: number;
  availableSlots: number;
}

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Session API methods
  async getSessions(gate?: 'In' | 'Out', limit: number = 100): Promise<SessionResponse[]> {
    const params = new URLSearchParams();
    if (gate) params.append('gate', gate);
    params.append('limit', limit.toString());

    const response = await fetch(`${this.baseURL}/api/sessions?${params}`);
    if (!response.ok) {
      throw new Error('Failed to fetch sessions');
    }
    return response.json();
  }

  async getSession(sessionId: string): Promise<SessionResponse> {
    const response = await fetch(`${this.baseURL}/api/sessions/${sessionId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch session');
    }
    return response.json();
  }

  async getInSessions(limit: number = 100): Promise<SessionResponse[]> {
    return this.getSessions('In', limit);
  }

  async getOutSessions(limit: number = 100): Promise<SessionResponse[]> {
    return this.getSessions('Out', limit);
  }

  // Parking slot API methods
  async getParkingSlots(): Promise<ParkingSlotResponse[]> {
    const response = await fetch(`${this.baseURL}/api/parking/slots`);
    if (!response.ok) {
      throw new Error('Failed to fetch parking slots');
    }
    return response.json();
  }

  async getAvailableSlots(): Promise<ParkingSlotResponse[]> {
    const response = await fetch(`${this.baseURL}/api/parking/slots/available`);
    if (!response.ok) {
      throw new Error('Failed to fetch available slots');
    }
    return response.json();
  }

  // Statistics and dashboard data
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      // Get current sessions
      const [inSessions, outSessions, allSlots, availableSlots] = await Promise.all([
        this.getInSessions(),
        this.getOutSessions(),
        this.getParkingSlots(),
        this.getAvailableSlots()
      ]);

      // Calculate current vehicles (In sessions where isOut = false)
      const currentVehicles = inSessions.filter(session => !session.session.isOut).length;
      
      // Calculate today's entries and exits
      const today = new Date().toISOString().split('T')[0];
      const todayEntries = inSessions.filter(session => 
        session.session.timestamp.startsWith(today)
      ).length;

      // Calculate occupancy rate
      const totalSlots = allSlots.length;
      const occupancyRate = totalSlots > 0 ? (currentVehicles / totalSlots) * 100 : 0;

      return {
        currentVehicles,
        totalEntries: inSessions.length,
        totalExits: outSessions.length,
        occupancyRate,
        totalParkedToday: todayEntries,
        availableSlots: availableSlots.length
      };
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      // Return default stats if API fails
      return {
        currentVehicles: 0,
        totalEntries: 0,
        totalExits: 0,
        occupancyRate: 0,
        totalParkedToday: 0,
        availableSlots: 0
      };
    }
  }

  // Get new session status
  async getNewSessionStatus(): Promise<IsNewSession | null> {
    try {
      const response = await fetch(`${this.baseURL}/api/sessions/new-session-status`);
      if (!response.ok) {
        return null;
      }
      return response.json();
    } catch (error) {
      console.error('Error fetching new session status:', error);
      return null;
    }
  }

  // Search and filter methods
  async searchSessionsByPlate(plateNumber: string): Promise<SessionResponse[]> {
    const sessions = await this.getSessions();
    return sessions.filter(session => 
      session.session.plateNumber?.toLowerCase().includes(plateNumber.toLowerCase())
    );
  }

  async getSessionsByDateRange(dateFrom: Date, dateTo: Date): Promise<SessionResponse[]> {
    const sessions = await this.getSessions();
    return sessions.filter(session => {
      const sessionDate = new Date(session.session.timestamp);
      return sessionDate >= dateFrom && sessionDate <= dateTo;
    });
  }

  // Convert session to vehicle format for compatibility with existing frontend
  sessionToVehicle(sessionResponse: SessionResponse): {
    id: string;
    licensePlate: string;
    faceId: string;
    entryTime: Date;
    exitTime: Date | null;
    status: 'parked' | 'exited';
    plateUrl: string;
    faceUrl: string;
    gate: string;
  } {
    const { session_id, session } = sessionResponse;
    return {
      id: session_id,
      licensePlate: session.plateNumber || 'Detecting...',
      faceId: session.faceIndex,
      entryTime: new Date(session.timestamp),
      exitTime: session.isOut ? new Date(session.timestamp) : null,
      status: session.isOut ? 'exited' : 'parked',
      plateUrl: session.plateUrl,
      faceUrl: session.faceUrl,
      gate: session.gate
    };
  }

  // Real-time polling for new sessions
  async pollForNewSessions(callback: (sessions: SessionResponse[]) => void, interval: number = 5000) {
    const poll = async () => {
      try {
        const newSessionStatus = await this.getNewSessionStatus();
        if (newSessionStatus?.status) {
          const recentSessions = await this.getSessions(undefined, 10);
          callback(recentSessions);
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    // Initial poll
    poll();
    
    // Set up interval
    return setInterval(poll, interval);
  }
}

export const apiService = new ApiService();
export default apiService;
