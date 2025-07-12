from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from google.cloud.firestore import DocumentSnapshot, CollectionReference
from app.db.firestore import get_collection, get_document, get_db
from app.models.session_model import (
    Session, SessionResponse, SessionCreateRequest, SessionUpdateRequest,
    IsNewSession, MatchingVerify, SessionMap, PlateMap, ParkingSlot,
    PlateDetectionRequest, FaceMatchingRequest, SessionForOutRequest
)

class SessionService:
    def __init__(self):
        self.collection_name = "Session"
    
    def create_session(self, session_data: SessionCreateRequest) -> str:
        """Create new session and return session ID"""
        session_id = str(uuid.uuid4())
        
        # For In sessions, automatically detect license plate number
        # TODO: Replace with actual AI plate detection service
        plate_number = None
        plate_detection_service = PlateDetectionService()
        plate_number = plate_detection_service._mock_plate_detection(session_data.plate_url)
        
        session = Session(
            plateUrl=session_data.plate_url,
            faceUrl=session_data.face_url,
            gate=session_data.gate,
            timestamp=datetime.now().isoformat(),
            isOut=False,
            faceIndex=session_data.face_index,
            plateNumber=plate_number  # Detected for In sessions, provided for Out sessions
        )
        
        # Convert to dict for Firestore
        session_dict = session.model_dump(by_alias=True)
        
        # Save to Firestore
        doc_ref = get_document(self.collection_name, session_id)
        doc_ref.set(session_dict)
        
        # If In session and has plate number, create plate mapping
        if session_data.gate == "In" and plate_number:
            plate_map_service = PlateMapService()
            plate_map_service.create_plate_map(plate_number, session_id)
        
        # If Out session, auto-checkout corresponding In session
        if session_data.gate == "Out" and session_data.face_index and plate_number:
            self._auto_checkout_matching_in_session(session_data.face_index, plate_number)
        
        # Update IsNewSession status
        self._update_new_session_status(session_id)
        
        # Log current vehicle count
        current_count = self.get_current_vehicles_count()
        if session_data.gate == "In":
            print(f"New vehicle entry. Current vehicles in parking: {current_count}")
        elif session_data.gate == "Out":
            print(f"Vehicle exit processed. Current vehicles in parking: {current_count}")
        
        return session_id
    
    def create_out_session(self, session_data: SessionForOutRequest) -> str:
        """Create exit session with entry session data"""
        session_id = str(uuid.uuid4())
        
        session = Session(
            plateUrl=session_data.plate_url,
            faceUrl=session_data.face_url,
            gate="Out",
            timestamp=datetime.now().isoformat(),
            isOut=False,
            faceIndex=session_data.face_index,  # From In session
            plateNumber=session_data.plate_number  # From In session
        )
        
        # Convert to dict for Firestore
        session_dict = session.model_dump(by_alias=True)
        
        # Save to Firestore
        doc_ref = get_document(self.collection_name, session_id)
        doc_ref.set(session_dict)
        
        # Auto-checkout corresponding In session if exists
        self._auto_checkout_matching_in_session(session_data.face_index, session_data.plate_number)
        
        # Log current vehicle count after checkout
        current_count = self.get_current_vehicles_count()
        print(f"Current vehicles in parking: {current_count}")
        
        # Update IsNewSession status
        self._update_new_session_status(session_id)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """Get session by ID"""
        doc_ref = get_document(self.collection_name, session_id)
        doc = doc_ref.get()
        
        if doc.exists:
            session_data = doc.to_dict()
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
            session = Session(**session_data)
            sessions.append(SessionResponse(session_id=doc.id, session=session))
        
        return sessions
    
    def update_session_out_status(self, session_id: str) -> bool:
        """Update session checkout status"""
        doc_ref = get_document(self.collection_name, session_id)
        doc_ref.update({"isOut": True})
        return True
    
    def update_plate_number(self, session_id: str, plate_number: str) -> bool:
        """Update plate number for session"""
        doc_ref = get_document(self.collection_name, session_id)
        doc_ref.update({"plateNumber": plate_number})
        return True
    
    def _update_new_session_status(self, session_id: str):
        """Update new session status"""
        status_doc = get_document("IsNewSession", "statusDoc")
        status_doc.set({
            "status": True,
            "sessionID": session_id
        })
    
    def get_new_session_status(self) -> Optional[IsNewSession]:
        """Get new session status"""
        status_doc = get_document("IsNewSession", "statusDoc")
        doc = status_doc.get()
        
        if doc.exists:
            data = doc.to_dict()
            return IsNewSession(**data)
        return None
    
    def clear_new_session_status(self):
        """Clear new session status"""
        status_doc = get_document("IsNewSession", "statusDoc")
        status_doc.set({
            "status": False,
            "sessionID": ""
        })
    
    def _auto_checkout_matching_in_session(self, face_index: str, plate_number: str):
        """Auto-checkout In sessions with matching face_index and plate_number"""
        try:
            collection_ref = get_collection(self.collection_name)
            
            # Find In sessions with same face_index and plate_number that haven't checked out (isOut = False)
            query = (collection_ref
                    .where("gate", "==", "In")
                    .where("isOut", "==", False)
                    .where("faceIndex", "==", face_index)
                    .where("plateNumber", "==", plate_number))
            
            docs = query.stream()
            
            checkout_count = 0
            for doc in docs:
                # Update isOut = True for corresponding In session
                doc.reference.update({"isOut": True})
                checkout_count += 1
                print(f"Auto-checkout session {doc.id} with face_index: {face_index}, plate: {plate_number}")
            
            if checkout_count > 0:
                current_count = self.get_current_vehicles_count()
                print(f"Auto-checkout completed. {checkout_count} session(s) processed. Current vehicles in parking: {current_count}")
                
        except Exception as e:
            print(f"Error in auto-checkout: {e}")

    def get_current_vehicles_count(self) -> int:
        """Count current vehicles in parking (In sessions that haven't checked out)"""
        try:
            collection_ref = get_collection(self.collection_name)
            
            # Count In sessions where isOut = False
            query = (collection_ref
                    .where("gate", "==", "In")
                    .where("isOut", "==", False))
            
            docs = list(query.stream())
            return len(docs)
            
        except Exception as e:
            print(f"Error counting current vehicles: {e}")
            return 0

    def process_out_session(self, session_data: SessionCreateRequest) -> str:
        """Process Out session with auto-checkout logic"""
        # Create Out session
        session_id = self.create_session(session_data)
        
        # If has face_index and plate_number, check and auto-checkout
        if session_data.face_index and hasattr(session_data, 'plate_number'):
            self._auto_checkout_matching_in_session(session_data.face_index, session_data.plate_number)
        
        return session_id
    
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


class PlateDetectionService:
    """Service for license plate detection and processing"""
    
    def __init__(self):
        self.session_service = SessionService()
        self.plate_map_service = PlateMapService()
    
    def detect_and_update_plate(self, session_id: str, plate_url: str) -> str:
        """Detect plate number from URL and update session"""
        # TODO: Replace with actual AI plate detection model
        # This would call your plate detection AI service
        plate_number = self._mock_plate_detection(plate_url)
        
        # Update session with detected plate number
        self.session_service.update_plate_number(session_id, plate_number)
        
        # Create plate mapping for lookup
        self.plate_map_service.create_plate_map(plate_number, session_id)
        
        return plate_number
    
    def _mock_plate_detection(self, plate_url: str) -> str:
        """Mock plate detection - replace with actual AI model"""
        # TODO: Implement actual plate detection AI logic here
        # This is a placeholder that should be replaced with:
        # 1. Load AI model (YOLO, OCR, etc.)
        # 2. Process image from plate_url
        # 3. Extract and return plate number
        import random
        import string
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        numbers = ''.join(random.choices(string.digits, k=4))
        # return f"{letters}-{numbers}"  # Random format
        return "QX-7018"
