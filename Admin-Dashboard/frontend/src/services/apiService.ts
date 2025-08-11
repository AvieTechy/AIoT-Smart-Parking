const API_BASE_URL = 'http://localhost:8000';

// Import types
import type { GroupedSession } from '../types/types';
import cacheService from './cacheService';
import authService from './authService';

// Session / data models
export interface Session {
  plateUrl: string;
  faceUrl: string;
  timestamp: string;
  gate: 'In' | 'Out';
  isOut: boolean;
  faceIndex: string;
  plateNumber?: string;
}
export interface SessionResponse { session_id: string; session: Session }
export interface IsNewSession { status: boolean; sessionID: string }
export interface MatchingVerify { sessionID: string; isMatch: boolean }
export interface SessionMap { entrySessionID: string; exitSessionID: string }
export interface ParkingSlot { slot_id: string; location_code: string; is_occupied: boolean; updated_at: string }
export interface ParkingSlotResponse { slot_id: string; slot: ParkingSlot }
export interface DashboardStats { current_vehicles: number; total_entries: number; available_slots: number; total_slots?: number }

class ApiService {
  private baseURL: string;
  constructor() { this.baseURL = API_BASE_URL }

  private async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    return authService.authenticatedRequest(url, options);
  }

  // ---------------- Sessions ----------------
  async getSessions(gate?: 'In' | 'Out', limit: number = 100): Promise<SessionResponse[]> {
    const cacheKey = cacheService.createKey('sessions', { gate, limit });
    const cached = cacheService.get(cacheKey);
    if (cached) return cached;
    const params = new URLSearchParams();
    if (gate) params.append('gate', gate);
    params.append('limit', limit.toString());
    const response = await fetch(`${this.baseURL}/api/sessions/?${params}`);
    if (!response.ok) throw new Error('Failed to fetch sessions');
    const data = await response.json();
    cacheService.set(cacheKey, data, 15);
    return data;
  }
  async getSession(sessionId: string): Promise<SessionResponse> {
    const response = await this.authenticatedFetch(`${this.baseURL}/api/sessions/${sessionId}`);
    if (!response.ok) throw new Error('Failed to fetch session');
    return response.json();
  }
  async getInSessions(limit: number = 100) { return this.getSessions('In', limit) }
  async getOutSessions(limit: number = 100) { return this.getSessions('Out', limit) }

  // Finalize exit AFTER verification (new API)
  async finalizeExitSession(exitSessionId: string): Promise<{success: boolean; message: string}> {
    const response = await fetch(`${this.baseURL}/api/sessions/finalize-exit/${exitSessionId}`, { method: 'POST' });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || data.message || 'Failed to finalize exit');
    // Bust caches because counts may change
    cacheService.clear();
    return data;
  }

  // ---------------- Parking Slots & Stats ----------------
  async getParkingSlots(): Promise<ParkingSlot[]> {
    const cacheKey = 'parking_slots';
    const cached = cacheService.get(cacheKey); if (cached) return cached;
    const response = await this.authenticatedFetch(`${this.baseURL}/api/parking/slots`);
    if (!response.ok) throw new Error('Failed to fetch parking slots');
    const data = await response.json(); cacheService.set(cacheKey, data, 20); return data;
  }
  async getParkingStats(): Promise<any> {
    const cacheKey = 'parking_stats';
    const cached = cacheService.get(cacheKey); if (cached) return cached;
    const response = await fetch(`${this.baseURL}/api/parking/stats`);
    if (!response.ok) throw new Error('Failed to fetch parking stats');
    const data = await response.json(); cacheService.set(cacheKey, data, 10); return data;
  }
  async getAvailableSlots(): Promise<ParkingSlot[]> {
    const cacheKey = 'available_slots';
    const cached = cacheService.get(cacheKey); if (cached) return cached;
    const response = await fetch(`${this.baseURL}/api/parking/slots/available`);
    if (!response.ok) throw new Error('Failed to fetch available slots');
    const data = await response.json(); cacheService.set(cacheKey, data, 15); return data;
  }
  async updateSlotOccupancy(slotId: string, isOccupied: boolean) {
    const response = await fetch(`${this.baseURL}/api/parking/slots/${slotId}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ is_occupied: isOccupied }) });
    if (!response.ok) throw new Error('Failed to update slot occupancy'); return response.json();
  }
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      const response = await fetch(`${this.baseURL}/api/dashboard/stats`);
      if (!response.ok) throw new Error('Failed');
      return response.json();
    } catch { return { current_vehicles: 0, total_entries: 0, available_slots: 0, total_slots: 10 } }
  }
  async updateTotalSlots(totalSlots: number) {
    const response = await fetch(`${this.baseURL}/api/dashboard/total-slots`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ total_slots: totalSlots }) });
    if (!response.ok) throw new Error((await response.json()).detail || 'Failed to update total slots');
    cacheService.clear(); return response.json();
  }

  // ---------------- Misc / Search ----------------
  async getNewSessionStatus(): Promise<IsNewSession | null> {
    try { const r = await fetch(`${this.baseURL}/api/sessions/new-session-status`); if (!r.ok) return null; return r.json(); } catch { return null }
  }
  async searchSessionsByPlate(plateNumber: string) {
    const sessions = await this.getSessions();
    return sessions.filter(s => s.session.plateNumber?.toLowerCase().includes(plateNumber.toLowerCase()));
  }
  async getSessionsByDateRange(dateFrom: Date, dateTo: Date) {
    const sessions = await this.getSessions();
    return sessions.filter(s => { const d = new Date(s.session.timestamp); return d >= dateFrom && d <= dateTo });
  }

  sessionToVehicle(sessionResponse: SessionResponse) {
    const { session_id, session } = sessionResponse;
    return { id: session_id, licensePlate: session.plateNumber || 'Detecting...', faceId: session.faceIndex, entryTime: new Date(session.timestamp), exitTime: session.isOut ? new Date(session.timestamp) : null, status: session.isOut ? 'exited' : 'parked', plateUrl: session.plateUrl, faceUrl: session.faceUrl, gate: session.gate };
  }

  // ---------------- Enhanced Grouping ----------------
  async getEnhancedGroupedSessions(): Promise<GroupedSession[]> {
    try {
      const response = await fetch(`${this.baseURL}/api/sessions/enhanced`);
      if (!response.ok) throw new Error('Failed to fetch enhanced sessions');
      const data = await response.json();
      return data.map((s: any): GroupedSession => ({
        faceId: s.faceId,
        licensePlate: s.licensePlate,
        entryTime: s.entryTime ? new Date(s.entryTime) : null,
        exitTime: s.exitTime ? new Date(s.exitTime) : null,
        status: s.status, duration: s.duration,
        entrySessionId: s.entrySessionId, entryGate: 'In', faceUrl: s.faceUrl, plateUrl: s.plateUrl,
        exitSessionId: s.exitSessionId, exitGate: 'Out', exitFaceUrl: s.exitFaceUrl, exitPlateUrl: s.exitPlateUrl,
        faceMatchVerified: s.faceMatchVerified, faceMatchResult: s.faceMatchResult
      }));
    } catch (e) {
      console.error('Enhanced grouping failed, fallback to naive:', e);
      return this.getGroupedSessions();
    }
  }

  // Fallback naive grouping (no verification) - keep semantics aligned with new statuses
  async getGroupedSessions(): Promise<GroupedSession[]> {
    try {
      const [inSessions, outSessions] = await Promise.all([this.getInSessions(), this.getOutSessions()]);
      const valid = (s: SessionResponse) => { const p = s.session.plateNumber; return p && p.trim() && p !== 'Detecting...' && p !== 'N/A' };
      const validIn = inSessions.filter(valid); const validOut = outSessions.filter(valid);
      const matched: GroupedSession[] = []; const usedIn = new Set<string>(); const usedOut = new Set<string>();
      const sortedOut = [...validOut].sort((a,b)=> new Date(b.session.timestamp).getTime()-new Date(a.session.timestamp).getTime());
      sortedOut.forEach(outS => {
        const outPlate = outS.session.plateNumber!.trim(); const outTime = new Date(outS.session.timestamp);
        const candidates = validIn.filter(inS => !usedIn.has(inS.session_id) && inS.session.plateNumber!.trim() === outPlate && new Date(inS.session.timestamp) <= outTime)
          .sort((a,b)=> new Date(b.session.timestamp).getTime()-new Date(a.session.timestamp).getTime());
        if (candidates.length) {
          const inS = candidates[0]; usedIn.add(inS.session_id); usedOut.add(outS.session_id);
          const inTime = new Date(inS.session.timestamp); const durationMinutes = Math.round((outTime.getTime()-inTime.getTime())/60000);
            matched.push({ faceId: inS.session.faceIndex || outS.session.faceIndex || '', licensePlate: outPlate, entryTime: inTime, exitTime: outTime, status: 'completed', entrySessionId: inS.session_id, entryGate: inS.session.gate, faceUrl: inS.session.faceUrl, plateUrl: inS.session.plateUrl, exitSessionId: outS.session_id, exitGate: outS.session.gate, exitFaceUrl: outS.session.faceUrl, exitPlateUrl: outS.session.plateUrl, duration: durationMinutes });
        }
      });
      // Unpaired IN => active
      validIn.filter(s=> !usedIn.has(s.session_id)).forEach(inS => matched.push({ faceId: inS.session.faceIndex || '', licensePlate: inS.session.plateNumber!.trim(), entryTime: new Date(inS.session.timestamp), exitTime: null, status: 'active', entrySessionId: inS.session_id, entryGate: inS.session.gate, faceUrl: inS.session.faceUrl, plateUrl: inS.session.plateUrl } as GroupedSession));
      // Unpaired OUT => failed (cannot verify entry)
      validOut.filter(s=> !usedOut.has(s.session_id)).forEach(outS => matched.push({ faceId: outS.session.faceIndex || '', licensePlate: outS.session.plateNumber!.trim(), entryTime: null, exitTime: new Date(outS.session.timestamp), status: 'failed', exitSessionId: outS.session_id, exitGate: outS.session.gate, exitFaceUrl: outS.session.faceUrl, exitPlateUrl: outS.session.plateUrl } as GroupedSession));
      return matched.sort((a,b)=> Math.max(a.entryTime?.getTime()||0,a.exitTime?.getTime()||0) < Math.max(b.entryTime?.getTime()||0,b.exitTime?.getTime()||0) ? 1 : -1);
    } catch (e) { console.error('Naive grouping error:', e); return [] }
  }

  // ---------------- Polling ----------------
  async pollForNewSessions(callback: (sessions: SessionResponse[]) => void, interval: number = 5000) {
    const poll = async () => { try { const st = await this.getNewSessionStatus(); if (st?.status) { const recent = await this.getSessions(undefined, 10); callback(recent) } } catch(e){ console.error('Polling error:', e) } };
    poll(); return setInterval(poll, interval);
  }
}

export const apiService = new ApiService();
export default apiService;
