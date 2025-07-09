from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.session_service import ParkingSlotService, SessionService

router = APIRouter(prefix="/api/parking", tags=["parking"])

# Initialize services
parking_service = ParkingSlotService()
session_service = SessionService()

class CreateSlotRequest(BaseModel):
    location_code: str
    is_occupied: bool = False

class UpdateSlotRequest(BaseModel):
    is_occupied: bool

@router.post("/slots", response_model=dict)
async def create_parking_slot(slot_data: CreateSlotRequest):
    """Create new parking slot"""
    try:
        slot_id = parking_service.create_parking_slot(
            location_code=slot_data.location_code,
            is_occupied=slot_data.is_occupied
        )
        return {
            "success": True,
            "slot_id": slot_id,
            "location_code": slot_data.location_code
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/slots", response_model=List[Dict[str, Any]])
async def get_all_parking_slots():
    """Get all parking slots"""
    try:
        slots = parking_service.get_all_slots()
        return slots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/slots/available", response_model=List[Dict[str, Any]])
async def get_available_slots():
    """Get available empty parking slots"""
    try:
        slots = parking_service.get_available_slots()
        return slots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/slots/{slot_id}", response_model=dict)
async def update_slot_occupancy(slot_id: str, update_data: UpdateSlotRequest):
    """Update slot occupancy status"""
    try:
        success = parking_service.update_slot_occupancy(slot_id, update_data.is_occupied)
        if success:
            return {
                "success": True,
                "slot_id": slot_id,
                "is_occupied": update_data.is_occupied
            }
        else:
            raise HTTPException(status_code=404, detail="Slot not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=dict)
async def get_parking_stats():
    """Get parking statistics including current vehicle count"""
    try:
        all_slots = parking_service.get_all_slots()
        available_slots = parking_service.get_available_slots()
        current_vehicles = session_service.get_current_vehicles_count()
        
        total_slots = len(all_slots)
        occupied_slots = total_slots - len(available_slots)
        occupancy_rate = (occupied_slots / total_slots * 100) if total_slots > 0 else 0
        
        return {
            "total_slots": total_slots,
            "occupied_slots": occupied_slots,
            "available_slots": len(available_slots),
            "occupancy_rate": round(occupancy_rate, 2),
            "current_vehicles": current_vehicles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
