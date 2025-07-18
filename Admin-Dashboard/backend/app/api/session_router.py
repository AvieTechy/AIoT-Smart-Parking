from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.session_model import (
    SessionResponse, SessionCreateRequest, SessionUpdateRequest
)
from app.services.session_service import (
    SessionService, PlateMapService
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# Initialize services
session_service = SessionService()
plate_map_service = PlateMapService()

@router.post("/", response_model=dict)
async def create_session(session_data: SessionCreateRequest):
    """Create new session - now requires plate_number in request"""
    try:
        session_id = session_service.create_session(session_data)
        
        # Get created session info
        session_response = session_service.get_session(session_id)
        
        response = {
            "success": True,
            "session_id": session_id,
            "message": f"Session created for gate: {session_data.gate}",
            "gate": session_data.gate,
            "plateNumber": session_data.plate_number,
            "faceIndex": session_data.face_index
        }
        
        # Add current vehicle count
        current_count = session_service.get_current_vehicles_count()
        response["current_vehicle_count"] = current_count
        
        if session_data.gate == "In":
            response["note"] = "Entry session created successfully"
        elif session_data.gate == "Out":
            response["note"] = "Exit session created, auto-checkout processed if matching In session found"
            
        return response
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

@router.patch("/{session_id}/update", response_model=dict)
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

@router.post("/auto-checkout", response_model=dict)
async def auto_checkout_session(face_index: str, plate_number: str):
    """Auto-checkout In sessions with matching face_index and plate_number"""
    try:
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

@router.get("/grouped", response_model=List[dict])
async def get_grouped_sessions():
    """Get sessions grouped by faceIndex and plateNumber for dashboard display"""
    try:
        # Get all sessions
        in_sessions = session_service.get_sessions_by_gate("In", 1000)
        out_sessions = session_service.get_sessions_by_gate("Out", 1000)
        all_sessions = in_sessions + out_sessions
        
        # Group by faceIndex + plateNumber
        grouped = {}
        for session_response in all_sessions:
            session = session_response.session
            key = f"{session.faceIndex}_{session.plateNumber}"
            
            if key not in grouped:
                grouped[key] = {
                    "faceId": session.faceIndex,
                    "licensePlate": session.plateNumber,
                    "entryTime": None,
                    "exitTime": None,
                    "status": "active",
                    "entrySessionId": None,
                    "exitSessionId": None,
                    "faceUrl": session.faceUrl,
                    "plateUrl": session.plateUrl,
                    "exitFaceUrl": None,
                    "exitPlateUrl": None
                }
            
            group = grouped[key]
            if session.gate == "In":
                group["entryTime"] = session.timestamp
                group["entrySessionId"] = session_response.session_id
                group["faceUrl"] = session.faceUrl
                group["plateUrl"] = session.plateUrl
            elif session.gate == "Out":
                group["exitTime"] = session.timestamp
                group["exitSessionId"] = session_response.session_id
                group["exitFaceUrl"] = session.faceUrl
                group["exitPlateUrl"] = session.plateUrl
                group["status"] = "completed"
        
        # Convert to list and sort by entry time (newest first)
        result = list(grouped.values())
        result.sort(key=lambda x: x["entryTime"] or "0000", reverse=True)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
