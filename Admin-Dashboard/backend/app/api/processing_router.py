from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.models.session_model import SessionCreateRequest, SessionForOutRequest
from app.services.session_service import (
    SessionService, PlateDetectionService,
    PlateMapService, MatchingVerifyService, SessionMapService
)

router = APIRouter(prefix="/api/processing", tags=["processing"])

# Initialize services
session_service = SessionService()
plate_detection_service = PlateDetectionService()
plate_map_service = PlateMapService()
matching_service = MatchingVerifyService()
session_map_service = SessionMapService()

@router.post("/entry-flow", response_model=dict)
async def process_entry_flow(session_data: SessionCreateRequest):
    """
    Simplified entry flow - just creates session without AI processing
    AI processing will be handled by separate team
    """
    try:
        if session_data.gate != "In":
            raise HTTPException(status_code=400, detail="This endpoint is only for entry sessions")
        
        # Create session with basic data
        session_id = session_service.create_session(session_data)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Entry session created successfully",
            "note": "AI processing (plate detection, face embedding) will be handled separately"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exit-flow", response_model=dict)
async def process_exit_flow(session_data: SessionForOutRequest):
    """
    Simplified exit flow - just creates session without AI processing
    AI processing will be handled by separate team
    """
    try:
        # Create exit session with information from entry session
        session_id = session_service.create_out_session(session_data)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Exit session created successfully",
            "note": "AI processing (face matching, verification) will be handled separately"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/processing-status", response_model=dict)
async def get_processing_status(session_id: str):
    """Kiểm tra trạng thái xử lý của session"""
    try:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Kiểm tra các trường đã được xử lý chưa
        has_plate_number = bool(session.session.plate_number)
        has_face_embedding = bool(session.session.face_embedding)
        
        processing_complete = has_plate_number and has_face_embedding
        
        return {
            "session_id": session_id,
            "processing_complete": processing_complete,
            "has_plate_number": has_plate_number,
            "has_face_embedding": has_face_embedding,
            "plate_number": session.session.plate_number,
            "gate": session.session.gate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plate/{plate_number}/matching-history", response_model=dict)
async def get_matching_history(plate_number: str):
    """Lấy lịch sử matching của một biển số xe"""
    try:
        # Tìm entry session
        entry_session_id = plate_map_service.get_session_by_plate(plate_number)
        if not entry_session_id:
            raise HTTPException(status_code=404, detail="No entry session found for this plate")
        
        entry_session = session_service.get_session(entry_session_id)
        
        return {
            "plate_number": plate_number,
            "entry_session": entry_session,
            "message": "Use specific endpoints to get exit sessions and matching results"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
