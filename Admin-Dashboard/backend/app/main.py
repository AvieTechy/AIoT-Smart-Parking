from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from app.api.session_router import router as session_router
from app.api.parking_router import router as parking_router
from app.api.auth_router import router as auth_router
from app.db.firestore import firestore_db

# Create FastAPI app
app = FastAPI(
    title="Smart Parking Admin API",
    description="API for Smart Parking Admin System with Firebase/Firestore",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(session_router)
app.include_router(parking_router)

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
