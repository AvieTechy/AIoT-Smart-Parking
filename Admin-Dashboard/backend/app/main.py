from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from app.api.session_router import router as session_router
from app.api.parking_router import router as parking_router
from app.api.auth_router import router as auth_router
from app.api.debug_router import router as debug_router
from app.db.firestore import firestore_db
from app.core.config import settings
from app.services.session_service import SessionService

# Create FastAPI app
app = FastAPI(
    title="Smart Parking Admin API",
    description="API for Smart Parking Admin System with Firebase/Firestore",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Use the property method
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(session_router)
app.include_router(parking_router)
app.include_router(debug_router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Smart Parking Admin API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check including Firebase connection"""
    try:
        # Test Firebase connection
        db = firestore_db.db
        # Try to read from a test collection
        test_ref = db.collection("_health_check").limit(1)
        list(test_ref.stream())  # This will fail if Firebase is not connected

        return {
            "status": "healthy",
            "firebase": "connected",
            "timestamp": "2025-06-26T00:00:00Z"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "firebase": "disconnected",
                "error": str(e),
                "timestamp": "2025-06-26T00:00:00Z"
            }
        )

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics with new business logic"""
    try:
        session_service = SessionService()
        stats = session_service.get_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/dashboard/total-slots")
async def update_total_slots(request: dict):
    """Update total parking slots"""
    try:
        total_slots = request.get("total_slots")
        if total_slots is None:
            raise HTTPException(status_code=400, detail="total_slots is required")

        if not isinstance(total_slots, int) or total_slots < 0:
            raise HTTPException(status_code=400, detail="total_slots must be a non-negative integer")

        session_service = SessionService()
        success = session_service.update_total_slots(total_slots)

        if success:
            # Return updated stats
            updated_stats = session_service.get_dashboard_stats()
            return {
                "success": True,
                "message": f"Total slots updated to {total_slots}",
                "updated_stats": updated_stats
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update total slots")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/debug")
async def get_dashboard_debug():
    """Debug endpoint to show stats calculation logic"""
    try:
        session_service = SessionService()

        # Get detailed info for debugging
        collection_ref = session_service.collection_name
        from app.db.firestore import get_collection, get_document

        # Get all sessions
        sessions_ref = get_collection(collection_ref)
        all_sessions = list(sessions_ref.stream())

        # Separate by gate
        in_sessions = []
        out_sessions = []

        for doc in all_sessions:
            doc_data = doc.to_dict()
            gate = doc_data.get("gate")
            plate_number = doc_data.get("plateNumber") or doc_data.get("platenumber")

            if gate == "In":
                in_sessions.append({
                    "id": doc.id[:8],
                    "plate": plate_number,
                    "timestamp": doc_data.get("timestamp")
                })
            elif gate == "Out":
                out_sessions.append({
                    "id": doc.id[:8],
                    "plate": plate_number,
                    "timestamp": doc_data.get("timestamp")
                })

        # Calculate current vehicles logic
        exited_plates = set()
        for out_session in out_sessions:
            if out_session["plate"]:
                exited_plates.add(out_session["plate"])

        current_vehicles_detail = []
        for in_session in in_sessions:
            if in_session["plate"] and in_session["plate"] not in exited_plates:
                current_vehicles_detail.append({
                    "plate": in_session["plate"],
                    "entry_time": in_session["timestamp"],
                    "status": "still_in_parking"
                })

        # Get Available Slots from ParkingMeta
        meta_doc_ref = get_document("ParkingMeta", "slotCounter")
        meta_doc = meta_doc_ref.get()
        parking_meta = meta_doc.to_dict() if meta_doc.exists else {}

        return {
            "logic_explanation": {
                "current_vehicles": "Count IN sessions that don't have corresponding OUT sessions with same plate number",
                "total_entries": "Count all sessions with gate='In'",
                "available_slots": "Calculated as total_slots - current_vehicles",
                "total_slots": "Read from ParkingMeta/slotCounter.total (editable by admin)"
            },
            "calculations": {
                "total_in_sessions": len(in_sessions),
                "total_out_sessions": len(out_sessions),
                "unique_exited_plates": len(exited_plates),
                "current_vehicles_count": len(current_vehicles_detail),
                "total_slots": parking_meta.get("total", 10),
                "available_slots_calculated": max(0, parking_meta.get("total", 10) - len(current_vehicles_detail))
            },
            "current_vehicles_detail": current_vehicles_detail,
            "exited_plates_list": list(exited_plates),
            "parking_meta": parking_meta,
            "final_stats": session_service.get_dashboard_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schema")
async def get_database_schema():
    """Get the database schema and collection structure"""
    return {
        "collections": {
            "Session": {
                "description": "Main session collection for vehicle entry/exit",
                "fields": {
                    "plateUrl": "str - URL to plate image on Cloudinary",
                    "faceUrl": "str - URL to face image on Cloudinary",
                    "timestamp": "str - ISO timestamp",
                    "gate": "str - 'In' or 'Out'",
                    "isOut": "bool - false when created, true when vehicle exits",
                    "faceIndex": "str - Face index identifier",
                    "plateNumber": "str|null - Detected plate number (initially null)"
                },
                "document_id": "Auto-generated UUID"
            },
            "PlateMap": {
                "description": "Maps plate numbers to session IDs",
                "fields": {
                    "sessionID": "str - Reference to Session document ID"
                },
                "document_id": "Plate number (e.g., 'AB-1234')"
            },
            "SessionMap": {
                "description": "Maps entry sessions to exit sessions",
                "fields": {
                    "entrySessionID": "str - Session ID for entry",
                    "exitSessionID": "str - Session ID for exit"
                },
                "document_id": "Auto-generated UUID"
            },
            "MatchingVerify": {
                "description": "Face matching verification results",
                "fields": {
                    "sessionID": "str - Exit session ID",
                    "isMatch": "bool - Whether faces matched"
                },
                "document_id": "Auto-generated UUID"
            },
            "IsNewSession": {
                "description": "Status tracking for new sessions",
                "fields": {
                    "status": "bool - True if new session exists",
                    "sessionID": "str - Current session ID"
                },
                "document_id": "statusDoc"
            },
            "ParkingSlot": {
                "description": "Parking slot management",
                "fields": {
                    "location_code": "str - Slot identifier (e.g., 'A1')",
                    "is_occupied": "bool - Occupancy status",
                    "updated_at": "timestamp - Last update time"
                },
                "document_id": "Auto-generated UUID"
            }
        },
        "workflow": {
            "entry": [
                "1. Device creates Session with gate='In', isOut=false",
                "2. AI processes plateUrl → detects plateNumber",
                "3. Create PlateMap[plateNumber] = sessionID"
            ],
            "exit": [
                "1. Device creates Session with gate='Out', isOut=false",
                "2. AI processes plateUrl → detects plateNumber",
                "3. Look up entry session: sessionID = PlateMap[plateNumber]",
                "4. AI processes face matching → create MatchingVerify",
                "5. Create SessionMap linking entry and exit sessions"
            ]
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG") else "Something went wrong"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
