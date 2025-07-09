from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.session_model import (
    SessionResponse, SessionCreateRequest, SessionForOutRequest,
    PlateDetectionRequest, FaceMatchingRequest, SessionUpdateRequest
)
from app.services.session_service import (
    SessionService, ParkingSlotService, SessionMapService,
    PlateMapService, MatchingVerifyService, PlateDetectionService
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# Initialize services
session_service = SessionService()
parking_service = ParkingSlotService()
session_map_service = SessionMapService()
plate_map_service = PlateMapService()
matching_service = MatchingVerifyService()
plate_detection_service = PlateDetectionService()

@router.post("/", response_model=dict)
async def create_session(session_data: SessionCreateRequest):
    """Create new session - In sessions will auto-detect plate number, Out sessions will auto-checkout matching In sessions"""
    try:
        session_id = session_service.create_session(session_data)
        
        # Get created session info to return plateNumber (if available)
        session_response = session_service.get_session(session_id)
        plate_number = session_response.session.plateNumber if session_response else None
        
        response = {
            "success": True,
            "session_id": session_id,
            "message": f"Session created for gate: {session_data.gate}",
            "gate": session_data.gate
        }
        
        if session_data.gate == "In" and plate_number:
            response["plateNumber"] = plate_number
            response["note"] = "Plate number automatically detected and saved"
            current_count = session_service.get_current_vehicles_count()
            response["current_vehicle_count"] = current_count
        elif session_data.gate == "In":
            response["note"] = "Plate number detection failed"
            current_count = session_service.get_current_vehicles_count()
            response["current_vehicle_count"] = current_count
        elif session_data.gate == "Out":
            response["plateNumber"] = plate_number
            response["note"] = "Exit session created, auto-checkout processed if matching In session found"
            current_count = session_service.get_current_vehicles_count()
            response["current_vehicle_count"] = current_count
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/out", response_model=dict)
async def create_out_session(session_data: SessionForOutRequest):
    """Create exit session with entry session data"""
    try:
        session_id = session_service.create_out_session(session_data)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Exit session created with entry session data",
            "note": "Use /process-exit endpoint for AI face matching processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session information by ID"""
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/", response_model=List[SessionResponse])
async def get_sessions(
    gate: Optional[str] = Query(None, description="Filter by gate type (In or Out)"),
    limit: int = Query(100, description="Limit number of results")
):
    """Get list of sessions"""
    try:
        if gate:
            sessions = session_service.get_sessions_by_gate(gate, limit)
        else:
            # Get all sessions
            in_sessions = session_service.get_sessions_by_gate("In", limit//2)
            out_sessions = session_service.get_sessions_by_gate("Out", limit//2)
            sessions = in_sessions + out_sessions
        
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{session_id}/out", response_model=dict)
async def mark_session_out(session_id: str):
    """Mark session as checked out"""
    try:
        success = session_service.update_session_out_status(session_id)
        if success:
            return {"success": True, "message": "Session marked as out"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plate/{plate_number}/session", response_model=dict)
async def get_session_by_plate(plate_number: str):
    """Get session by license plate number"""
    try:
        session_id = plate_map_service.get_session_by_plate(plate_number)
        if not session_id:
            raise HTTPException(status_code=404, detail="No session found for this plate number")
        
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session data not found")
        
        return {
            "plate_number": plate_number,
            "session": session
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/matching-verify", response_model=dict)
async def create_matching_verify(session_id: str, is_match: bool):
    """Save face matching verification result"""
    try:
        result_id = matching_service.create_matching_result(session_id, is_match)
        return {
            "success": True,
            "result_id": result_id,
            "session_id": session_id,
            "is_match": is_match
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session-map", response_model=dict)
async def create_session_mapping(entry_session_id: str, exit_session_id: str):
    """Create mapping between entry and exit sessions"""
    try:
        map_id = session_map_service.create_session_map(entry_session_id, exit_session_id)
        return {
            "success": True,
            "map_id": map_id,
            "entry_session_id": entry_session_id,
            "exit_session_id": exit_session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plate-detection", response_model=dict)
async def process_plate_detection(request: PlateDetectionRequest):
    """Xử lý nhận diện biển số và cập nhật session (độc lập)"""
    try:
        plate_number = plate_detection_service.detect_and_update_plate(
            request.session_id, request.plate_url
        )
        return {
            "success": True,
            "session_id": request.session_id,
            "plate_number": plate_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-session", response_model=dict)
async def update_session_fields(session_id: str, update_data: SessionUpdateRequest):
    """Update plate number of the session"""
    try:
        if update_data.plate_number is not None:
            session_service.update_plate_number(session_id, update_data.plate_number)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Session updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/new-session-status", response_model=dict)
async def get_new_session_status():
    """Get new session status"""
    try:
        status = session_service.get_new_session_status()
        if status:
            return {
                "status": status.status,
                "session_id": status.session_id
            }
        else:
            return {
                "status": False,
                "session_id": ""
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-new-session-status", response_model=dict)
async def clear_new_session_status():
    """Clear new session status"""
    try:
        session_service.clear_new_session_status()
        return {
            "success": True,
            "message": "New session status cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current-vehicle-count", response_model=dict)
async def get_current_vehicle_count():
    """Get current number of vehicles in parking"""
    try:
        current_count = session_service.get_current_vehicles_count()
        return {
            "success": True,
            "current_vehicle_count": current_count,
            "message": f"Current vehicles in parking: {current_count}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-and-update-matching", response_model=dict)
async def check_and_update_matching_sessions(face_index: str, plate_number: str):
    """Check and update In sessions matching with face_index and plate_number"""
    try:
        result = session_service.check_and_update_matching_sessions(face_index, plate_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-checkout", response_model=dict)
async def auto_checkout_session(face_index: str, plate_number: str):
    """Auto-checkout In sessions with matching face_index and plate_number"""
    try:
        # Call private method through wrapper
        result = session_service.check_and_update_matching_sessions(face_index, plate_number)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "updated_sessions": result["updated_sessions"],
                "current_vehicle_count": result["current_vehicle_count"]
            }
        else:
            return {
                "success": False,
                "message": result["message"],
                "current_vehicle_count": result["current_vehicle_count"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
