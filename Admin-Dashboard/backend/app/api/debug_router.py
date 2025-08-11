from fastapi import APIRouter
from app.services.session_service import SessionService

router = APIRouter(prefix="/api/debug", tags=["debug"])

@router.get("/vehicle-count")
async def debug_vehicle_count():
    """Debug endpoint to check vehicle count calculation"""
    session_service = SessionService()

    try:
        # Get raw count
        vehicle_count = session_service.get_current_vehicles_count()

        # Get some sample sessions for debugging
        from app.db.firestore import get_collection
        collection_ref = get_collection("Session")

        # Get In sessions with isOut=False
        in_sessions_query = collection_ref.where("gate", "==", "In").where("isOut", "==", False).limit(10)
        in_sessions_docs = list(in_sessions_query.stream())

        sample_sessions = []
        for doc in in_sessions_docs:
            data = doc.to_dict()
            sample_sessions.append({
                "id": doc.id,
                "gate": data.get("gate"),
                "isOut": data.get("isOut"),
                "timestamp": str(data.get("timestamp")),
                "plateNumber": data.get("plateNumber")
            })

        return {
            "current_vehicles_count": vehicle_count,
            "sample_active_sessions": sample_sessions,
            "sample_count": len(sample_sessions)
        }

    except Exception as e:
        return {
            "error": str(e),
            "current_vehicles_count": 0,
            "sample_active_sessions": [],
            "sample_count": 0
        }

@router.get("/session-pairing")
async def debug_session_pairing():
    """Debug endpoint to test exact plateNumber session pairing logic"""
    from app.db.firestore import get_collection
    from datetime import datetime

    try:
        collection_ref = get_collection("Session")

        # Get In and Out sessions
        in_sessions_query = collection_ref.where("gate", "==", "In").limit(500)
        out_sessions_query = collection_ref.where("gate", "==", "Out").limit(500)

        in_sessions_docs = list(in_sessions_query.stream())
        out_sessions_docs = list(out_sessions_query.stream())

        # Convert to dict and filter for valid plate numbers
        valid_in_sessions = []
        valid_out_sessions = []

        for doc in in_sessions_docs:
            data = doc.to_dict()
            # Fix field mapping: Firebase has 'platenumber' (lowercase)
            plate_number = data.get("plateNumber") or data.get("platenumber")
            if plate_number and plate_number.strip() and plate_number != "Detecting..." and plate_number != "N/A":
                valid_in_sessions.append({
                    "session_id": doc.id,
                    "plateNumber": plate_number.strip(),
                    "timestamp": data["timestamp"],
                    "faceUrl": data.get("faceUrl", ""),
                    "plateUrl": data.get("plateUrl", "")
                })

        for doc in out_sessions_docs:
            data = doc.to_dict()
            # Fix field mapping: Firebase has 'platenumber' (lowercase)
            plate_number = data.get("plateNumber") or data.get("platenumber")
            if plate_number and plate_number.strip() and plate_number != "Detecting..." and plate_number != "N/A":
                valid_out_sessions.append({
                    "session_id": doc.id,
                    "plateNumber": plate_number.strip(),
                    "timestamp": data["timestamp"],
                    "faceUrl": data.get("faceUrl", ""),
                    "plateUrl": data.get("plateUrl", "")
                })

        # Pairing logic: 1-1 exact plateNumber matching
        matched_pairs = []
        used_in_session_ids = set()

        # Sort OUT sessions by timestamp (newest first)
        valid_out_sessions.sort(key=lambda x: x["timestamp"], reverse=True)

        # For each OUT session, find nearest IN session with exact same plate number
        for out_session in valid_out_sessions:
            out_plate = out_session["plateNumber"]
            out_time = out_session["timestamp"]

            # Find candidate IN sessions with exact same plate number
            candidate_in_sessions = [
                s for s in valid_in_sessions
                if s["plateNumber"] == out_plate  # Exact match
                and s["session_id"] not in used_in_session_ids  # Not already used
                and s["timestamp"] <= out_time  # IN must be before OUT
            ]

            if candidate_in_sessions:
                # Sort by timestamp descending to get nearest (most recent) IN session
                candidate_in_sessions.sort(key=lambda x: x["timestamp"], reverse=True)
                nearest_in = candidate_in_sessions[0]

                # Mark as used (1-1 pairing)
                used_in_session_ids.add(nearest_in["session_id"])

                # Calculate duration
                duration_seconds = (out_time - nearest_in["timestamp"]).total_seconds() if hasattr(out_time, 'total_seconds') else 0
                duration_minutes = int(duration_seconds / 60) if duration_seconds > 0 else 0

                matched_pairs.append({
                    "plateNumber": out_plate,
                    "inSession": {
                        "id": nearest_in["session_id"][:12] + "...",
                        "timestamp": str(nearest_in["timestamp"]),
                        "faceUrl": nearest_in["faceUrl"],
                        "plateUrl": nearest_in["plateUrl"]
                    },
                    "outSession": {
                        "id": out_session["session_id"][:12] + "...",
                        "timestamp": str(out_session["timestamp"]),
                        "faceUrl": out_session["faceUrl"],
                        "plateUrl": out_session["plateUrl"]
                    },
                    "duration_minutes": duration_minutes
                })

        # Group by plate number to show statistics
        plate_stats = {}
        for pair in matched_pairs:
            plate = pair["plateNumber"]
            if plate not in plate_stats:
                plate_stats[plate] = 0
            plate_stats[plate] += 1

        return {
            "summary": {
                "total_in_sessions": len(valid_in_sessions),
                "total_out_sessions": len(valid_out_sessions),
                "matched_pairs_count": len(matched_pairs),
                "unique_plates_matched": len(plate_stats)
            },
            "plate_statistics": dict(list(plate_stats.items())[:10]),  # Top 10 plates
            "sample_matched_pairs": matched_pairs[:10],  # First 10 pairs for inspection
            "pairing_logic": "1-1 exact plateNumber matching: each OUT session paired with nearest IN session"
        }

    except Exception as e:
        return {
            "error": str(e),
            "summary": {
                "total_in_sessions": 0,
                "total_out_sessions": 0,
                "matched_pairs_count": 0,
                "unique_plates_matched": 0
            },
            "plate_statistics": {},
            "sample_matched_pairs": []
        }
