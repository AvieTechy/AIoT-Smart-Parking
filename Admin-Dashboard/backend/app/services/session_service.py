from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from app.db.firestore import get_collection, get_document, get_db
from app.models.session_model import (
    Session, SessionResponse, SessionCreateRequest, SessionUpdateRequest,
    MatchingVerify, SessionMap, PlateMap, ParkingSlot
)
from app.services.session_pairing_service import SessionPairingService

def _convert_session_data(session_data: dict) -> dict:
    """Convert Firebase session data to format compatible with Pydantic model"""
    # Convert timestamp
    if session_data.get("timestamp") and hasattr(session_data["timestamp"], "isoformat"):
        # Convert DatetimeWithNanoseconds to string
        session_data["timestamp"] = session_data["timestamp"].isoformat()
    elif session_data.get("timestamp") and hasattr(session_data["timestamp"], "strftime"):
        # Convert datetime to string
        session_data["timestamp"] = session_data["timestamp"].isoformat()

    # Fix plateNumber field mapping: Firebase has 'platenumber' (lowercase)
    if "platenumber" in session_data and "plateNumber" not in session_data:
        session_data["plateNumber"] = session_data["platenumber"]

    return session_data

class SessionService:
    def __init__(self):
        self.collection_name = "Session"

    def create_session(self, session_data: SessionCreateRequest) -> str:
        """Create new session and return session ID. (No longer auto-checks out on Out session creation)"""
        session_id = str(uuid.uuid4())
        session = Session(
            plateUrl=session_data.plate_url,
            faceUrl=session_data.face_url,
            gate=session_data.gate,
            timestamp=datetime.now().isoformat(),
            isOut=False,
            faceIndex=session_data.face_index,
            plateNumber=session_data.plate_number
        )
        session_dict = session.model_dump(by_alias=True)
        doc_ref = get_document(self.collection_name, session_id)
        doc_ref.set(session_dict)

        # Plate mapping (fast lookup)
        plate_map_service = PlateMapService()
        plate_map_service.create_plate_map(session_data.plate_number, session_id)

        # NOTE: We removed the auto-checkout here to avoid premature completion before verification.
        # Verification + mapping will be handled explicitly via finalize_exit_session.

        current_count = self.get_current_vehicles_count()
        if session_data.gate == "In":
            print(f"New vehicle entry. Current vehicles in parking: {current_count}")
        elif session_data.gate == "Out":
            print(f"Exit session recorded (pending verification). Current vehicles in parking: {current_count}")
        return session_id

    def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """Get session by ID"""
        doc_ref = get_document(self.collection_name, session_id)
        doc = doc_ref.get()

        if doc.exists:
            session_data = doc.to_dict()
            session_data = _convert_session_data(session_data)
            session = Session(**session_data)
            return SessionResponse(session_id=session_id, session=session)
        return None

    def get_sessions_by_gate(self, gate: str, limit: int = 100) -> List[SessionResponse]:
        """Get sessions by gate type"""
        collection_ref = get_collection(self.collection_name)
        query = collection_ref.where("gate", "==", gate).limit(limit)
        docs = query.stream()

        sessions = []
        for doc in docs:
            session_data = doc.to_dict()
            session_data = _convert_session_data(session_data)
            session = Session(**session_data)
            sessions.append(SessionResponse(session_id=doc.id, session=session))

        return sessions

    def update_plate_number(self, session_id: str, plate_number: str) -> bool:
        """Update plate number for session"""
        doc_ref = get_document(self.collection_name, session_id)
        doc_ref.update({"plateNumber": plate_number})
        return True

    def finalize_exit_session(self, exit_session_id: str) -> Dict[str, Any]:
        """Finalize an exit after successful face matching verification.
        Steps:
          1. Ensure exit session exists and gate == 'Out'
          2. Find MatchingVerify with sessionID == exit_session_id and isMatch == True
          3. Locate the most recent unmatched In session (isOut == False) with same plateNumber & faceIndex before exit timestamp
          4. Mark that In session isOut = True, create SessionMap, return result
        """
        try:
            exit_doc_ref = get_document(self.collection_name, exit_session_id)
            exit_doc = exit_doc_ref.get()
            if not exit_doc.exists:
                return {"success": False, "message": "Exit session not found"}
            exit_data = exit_doc.to_dict()
            if exit_data.get("gate") != "Out":
                return {"success": False, "message": "Session is not an exit session"}

            plate_number = exit_data.get("plateNumber") or exit_data.get("platenumber")
            face_index = exit_data.get("faceIndex")
            if not plate_number or not face_index:
                return {"success": False, "message": "Exit session missing plateNumber or faceIndex"}

            # 2. Verification check
            verify_ref = get_collection("MatchingVerify")
            verify_query = verify_ref.where("sessionID", "==", exit_session_id).where("isMatch", "==", True)
            verify_docs = list(verify_query.stream())
            if not verify_docs:
                return {"success": False, "message": "No successful verification for this exit session"}

            # Parse exit timestamp
            exit_time = exit_data.get("timestamp")
            if hasattr(exit_time, 'isoformat'):
                exit_time_value = exit_time
            else:
                try:
                    exit_time_value = datetime.fromisoformat(str(exit_time))
                except Exception:
                    exit_time_value = datetime.min

            # 3. Locate candidate In sessions
            collection_ref = get_collection(self.collection_name)
            in_query = (collection_ref
                        .where("gate", "==", "In")
                        .where("isOut", "==", False)
                        .where("plateNumber", "==", plate_number)
                        .where("faceIndex", "==", face_index))
            candidates = []
            for doc in in_query.stream():
                data = doc.to_dict()
                ts = data.get("timestamp")
                if hasattr(ts, 'isoformat'):
                    ts_val = ts
                else:
                    try:
                        ts_val = datetime.fromisoformat(str(ts))
                    except Exception:
                        ts_val = datetime.min
                if ts_val <= exit_time_value:
                    candidates.append((doc.id, ts_val))

            if not candidates:
                return {"success": False, "message": "No matching entry session found to finalize"}

            # Most recent candidate before exit
            candidates.sort(key=lambda x: x[1], reverse=True)
            entry_session_id, entry_time_val = candidates[0]

            # 4. Mark entry isOut & create SessionMap
            entry_ref = get_document(self.collection_name, entry_session_id)
            entry_ref.update({"isOut": True})

            # Create mapping if not existing
            existing_map = self._find_existing_map(entry_session_id, exit_session_id)
            if not existing_map:
                session_map_service = SessionMapService()
                map_id = session_map_service.create_session_map(entry_session_id, exit_session_id)
            else:
                map_id = existing_map

            current_count = self.get_current_vehicles_count()
            return {
                "success": True,
                "message": "Exit finalized successfully",
                "entry_session_id": entry_session_id,
                "exit_session_id": exit_session_id,
                "session_map_id": map_id,
                "current_vehicle_count": current_count
            }
        except Exception as e:
            return {"success": False, "message": f"Error finalizing exit: {e}"}

    def _find_existing_map(self, entry_id: str, exit_id: str) -> Optional[str]:
        try:
            maps_ref = get_collection("SessionMap")
            query = maps_ref.where("entrySessionID", "==", entry_id).where("exitSessionID", "==", exit_id)
            docs = list(query.stream())
            if docs:
                return docs[0].id
            return None
        except Exception:
            return None

    def get_current_vehicles_count(self) -> int:
        """Count current vehicles in parking using face matching verification"""
        try:
            pairing_service = SessionPairingService()
            result = pairing_service.get_current_vehicles_accurate()

            count = result.get("count", 0)
            print(f"Current vehicles in parking: {count} (verified exits: {result.get('verified_exits', 0)})")

            return count

        except Exception as e:
            print(f"Error counting current vehicles: {e}")
            return 0

    def get_total_entries_count(self) -> int:
        """Count total entries (all In sessions)"""
        try:
            collection_ref = get_collection(self.collection_name)

            # Count all In sessions
            query = collection_ref.where("gate", "==", "In")
            docs = list(query.stream())
            return len(docs)

        except Exception as e:
            print(f"Error counting total entries: {e}")
            return 0

    def get_available_slots_count(self) -> int:
        """Get available slots count calculated as total - current_vehicles"""
        try:
            total_slots = self.get_total_slots_count()
            current_vehicles = self.get_current_vehicles_count()
            available = max(0, total_slots - current_vehicles)  # Don't go negative

            # Update the available count in Firebase for consistency
            self._update_available_slots_in_firebase(available)

            return available

        except Exception as e:
            print(f"Error calculating available slots count: {e}")
            return 0

    def get_total_slots_count(self) -> int:
        """Get total slots count from ParkingMeta/slotCounter"""
        try:
            doc_ref = get_document("ParkingMeta", "slotCounter")
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                return data.get("total", 10)  # Default to 10 if not set
            else:
                # Create default document if it doesn't exist
                self._create_default_slot_counter()
                return 10

        except Exception as e:
            print(f"Error getting total slots count: {e}")
            return 10

    def update_total_slots(self, total_slots: int) -> bool:
        """Update total slots count in ParkingMeta/slotCounter"""
        try:
            if total_slots < 0:
                raise ValueError("Total slots cannot be negative")

            doc_ref = get_document("ParkingMeta", "slotCounter")

            # Calculate new available count
            current_vehicles = self.get_current_vehicles_count()
            available = max(0, total_slots - current_vehicles)

            # Update both total and available
            doc_ref.set({
                "total": total_slots,
                "available": available
            }, merge=True)

            print(f"Updated total slots to {total_slots}, available: {available}")
            return True

        except Exception as e:
            print(f"Error updating total slots: {e}")
            return False

    def _update_available_slots_in_firebase(self, available: int):
        """Update available slots count in Firebase"""
        try:
            doc_ref = get_document("ParkingMeta", "slotCounter")
            doc_ref.set({"available": available}, merge=True)
        except Exception as e:
            print(f"Error updating available slots in Firebase: {e}")

    def _create_default_slot_counter(self):
        """Create default slotCounter document"""
        try:
            doc_ref = get_document("ParkingMeta", "slotCounter")
            doc_ref.set({
                "total": 10,
                "available": 10
            })
            print("Created default slotCounter document")
        except Exception as e:
            print(f"Error creating default slotCounter: {e}")

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        try:
            current_vehicles = self.get_current_vehicles_count()
            total_entries = self.get_total_entries_count()
            available_slots = self.get_available_slots_count()
            total_slots = self.get_total_slots_count()

            return {
                "current_vehicles": current_vehicles,
                "total_entries": total_entries,
                "available_slots": available_slots,
                "total_slots": total_slots
            }

        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                "current_vehicles": 0,
                "total_entries": 0,
                "available_slots": 0,
                "total_slots": 10
            }

    def check_and_update_matching_sessions(self, face_index: str, plate_number: str) -> Dict[str, Any]:
        """Check and update sessions matching with face_index and plate_number"""
        try:
            collection_ref = get_collection(self.collection_name)

            # Find In sessions with same face_index and plate_number that haven't checked out
            query = (collection_ref
                    .where("gate", "==", "In")
                    .where("isOut", "==", False)
                    .where("faceIndex", "==", face_index)
                    .where("plateNumber", "==", plate_number))

            docs = list(query.stream())

            if docs:
                # Update matching sessions
                updated_sessions = []
                for doc in docs:
                    doc.reference.update({"isOut": True})
                    updated_sessions.append(doc.id)

                # Update current vehicle count
                current_count = self.get_current_vehicles_count()

                return {
                    "success": True,
                    "updated_sessions": updated_sessions,
                    "current_vehicle_count": current_count,
                    "message": f"Updated {len(updated_sessions)} session(s). Current vehicles in parking: {current_count}"
                }
            else:
                return {
                    "success": False,
                    "updated_sessions": [],
                    "current_vehicle_count": self.get_current_vehicles_count(),
                    "message": "No matching In session found to checkout"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error checking matching sessions: {e}"
            }

class ParkingSlotService:
    def __init__(self):
        self.collection_name = "ParkingSlot"

    def create_parking_slot(self, location_code: str, is_occupied: bool = False) -> str:
        """Create new parking slot"""
        slot_id = str(uuid.uuid4())

        slot = ParkingSlot(
            location_code=location_code,
            is_occupied=is_occupied,
            updated_at=datetime.now()
        )

        slot_dict = slot.model_dump()
        slot_dict['updated_at'] = slot.updated_at

        doc_ref = get_document(self.collection_name, slot_id)
        doc_ref.set(slot_dict)

        return slot_id

    def get_all_slots(self) -> List[Dict[str, Any]]:
        """Get all parking slots"""
        collection_ref = get_collection(self.collection_name)
        docs = collection_ref.stream()

        slots = []
        for doc in docs:
            slot_data = doc.to_dict()
            slot_data['slot_id'] = doc.id
            slots.append(slot_data)

        return slots

    def update_slot_occupancy(self, slot_id: str, is_occupied: bool) -> bool:
        """Update slot occupancy status"""
        doc_ref = get_document(self.collection_name, slot_id)
        doc_ref.update({
            "is_occupied": is_occupied,
            "updated_at": datetime.now()
        })
        return True

    def get_available_slots(self) -> List[Dict[str, Any]]:
        """Get available empty slots"""
        collection_ref = get_collection(self.collection_name)
        query = collection_ref.where("is_occupied", "==", False)
        docs = query.stream()

        slots = []
        for doc in docs:
            slot_data = doc.to_dict()
            slot_data['slot_id'] = doc.id
            slots.append(slot_data)

        return slots

class SessionMapService:
    def __init__(self):
        self.collection_name = "SessionMap"

    def create_session_map(self, entry_session_id: str, exit_session_id: str) -> str:
        """Create mapping between entry and exit session"""
        map_id = str(uuid.uuid4())

        session_map = SessionMap(
            entrySessionID=entry_session_id,
            exitSessionID=exit_session_id
        )

        doc_ref = get_document(self.collection_name, map_id)
        doc_ref.set(session_map.model_dump(by_alias=True))

        return map_id

class PlateMapService:
    def __init__(self):
        self.collection_name = "PlateMap"

    def create_plate_map(self, plate_number: str, session_id: str):
        """Create mapping from license plate to session ID"""
        # Use plate number as document ID
        doc_ref = get_document(self.collection_name, plate_number)
        doc_ref.set({"sessionID": session_id})

    def get_session_by_plate(self, plate_number: str) -> Optional[str]:
        """Get session ID by license plate number"""
        doc_ref = get_document(self.collection_name, plate_number)
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            return data.get("sessionID")
        return None

class MatchingVerifyService:
    def __init__(self):
        self.collection_name = "MatchingVerify"

    def create_matching_result(self, session_id: str, is_match: bool) -> str:
        """Save face matching verification result for exit"""
        result_id = str(uuid.uuid4())

        matching_verify = MatchingVerify(
            sessionID=session_id,
            isMatch=is_match
        )

        doc_ref = get_document(self.collection_name, result_id)
        doc_ref.set(matching_verify.model_dump(by_alias=True))

        return result_id
