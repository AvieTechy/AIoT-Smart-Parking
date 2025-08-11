from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.db.firestore import get_collection, get_document

class SessionPairingService:
    """
    Advanced session pairing service that uses both plate number and face matching
    to accurately determine vehicle status and prevent false matches.
    """

    def __init__(self):
        self.session_collection = "Session"
        self.matching_verify_collection = "MatchingVerify"
        self.session_map_collection = "SessionMap"

    def get_verified_session_pairs(self) -> List[Dict[str, Any]]:
        """
        Get all verified session pairs using face matching verification.
        Returns list of paired sessions with verification status.
        """
        try:
            # Get all session maps (entry-exit pairs)
            session_maps = self._get_all_session_maps()

            # Get all matching verifications
            matching_verifications = self._get_all_matching_verifications()

            # Get all sessions
            all_sessions = self._get_all_sessions()
            sessions_dict = {doc.id: doc.to_dict() for doc in all_sessions}

            verified_pairs = []

            for session_map in session_maps:
                map_data = session_map.to_dict()
                entry_id = map_data.get("entrySessionID")
                exit_id = map_data.get("exitSessionID")

                if not entry_id or not exit_id:
                    continue

                entry_session = sessions_dict.get(entry_id)
                exit_session = sessions_dict.get(exit_id)

                if not entry_session or not exit_session:
                    continue

                # Find matching verification for this exit session
                verification = self._find_verification_for_session(exit_id, matching_verifications)

                pair_info = {
                    "entry_session_id": entry_id,
                    "exit_session_id": exit_id,
                    "entry_session": entry_session,
                    "exit_session": exit_session,
                    "face_match_verified": verification is not None,
                    "face_match_result": verification.get("isMatch") if verification else None,
                    "is_valid_pair": self._is_valid_session_pair(entry_session, exit_session, verification)
                }

                verified_pairs.append(pair_info)

            return verified_pairs

        except Exception as e:
            print(f"Error getting verified session pairs: {e}")
            return []

    def get_current_vehicles_accurate(self) -> Dict[str, Any]:
        """
        Get accurate count of current vehicles using face matching verification.
        """
        try:
            # Get all verified pairs
            verified_pairs = self.get_verified_session_pairs()

            # Get all IN sessions
            in_sessions = self._get_sessions_by_gate("In")

            # Track which entry sessions have valid exits
            exited_entry_sessions = set()

            for pair in verified_pairs:
                # Only count as exited if face matching passed
                if pair["is_valid_pair"] and pair["face_match_result"]:
                    exited_entry_sessions.add(pair["entry_session_id"])

            # Count vehicles still in parking
            current_vehicles = []
            for doc in in_sessions:
                session_data = doc.to_dict()

                # Skip if this entry session has a verified exit
                if doc.id in exited_entry_sessions:
                    continue

                # Check if session has valid plate number
                plate_number = session_data.get("plateNumber") or session_data.get("platenumber")
                if not plate_number or plate_number in ["N/A", "Detecting...", ""]:
                    continue

                current_vehicles.append({
                    "session_id": doc.id,
                    "face_index": session_data.get("faceIndex"),
                    "plate_number": plate_number,
                    "entry_time": session_data.get("timestamp"),
                    "status": "currently_parked"
                })

            return {
                "count": len(current_vehicles),
                "vehicles": current_vehicles,
                "verified_exits": len(exited_entry_sessions),
                "total_entries": len(in_sessions)
            }

        except Exception as e:
            print(f"Error calculating current vehicles: {e}")
            return {"count": 0, "vehicles": [], "verified_exits": 0, "total_entries": 0}

    def get_enhanced_grouped_sessions(self) -> List[Dict[str, Any]]:
        """
        Get enhanced grouped sessions with proper verification status.
        """
        try:
            # Get verified pairs
            verified_pairs = self.get_verified_session_pairs()

            # Get all sessions
            all_sessions = self._get_all_sessions()
            sessions_dict = {doc.id: doc.to_dict() for doc in all_sessions}

            grouped_sessions = []
            used_session_ids = set()

            # Process verified pairs first
            for pair in verified_pairs:
                entry_session = pair["entry_session"]
                exit_session = pair["exit_session"]

                # If the pair is NOT valid (e.g. plate/face mismatch, timestamp issue),
                # skip grouping them together so they will be treated as separate
                # unmatched sessions below (entry -> active, exit -> failed). This keeps
                # current_vehicles count consistent with visible 'active' sessions.
                if not (pair["is_valid_pair"] and pair["face_match_result"]):
                    # We only skip pairing; DO NOT mark IDs as used yet so they fall into
                    # the unmatched processing later.
                    continue

                # Convert session data
                entry_time = self._parse_timestamp(entry_session.get("timestamp"))
                exit_time = self._parse_timestamp(exit_session.get("timestamp"))

                plate_number = (entry_session.get("plateNumber") or
                              entry_session.get("platenumber") or
                              exit_session.get("plateNumber") or
                              exit_session.get("platenumber") or "Unknown")

                face_index = (entry_session.get("faceIndex") or
                             exit_session.get("faceIndex") or "Unknown")

                # Determine status based on verification (only completed reaches here)
                status = "completed"

                duration = None
                if entry_time and exit_time:
                    duration = int((exit_time - entry_time).total_seconds() / 60)

                grouped_session = {
                    "face_id": face_index,
                    "license_plate": plate_number,
                    "entry_time": entry_time,
                    "exit_time": exit_time,
                    "status": status,
                    "duration": duration,

                    # Entry session data
                    "entry_session_id": pair["entry_session_id"],
                    "face_url": entry_session.get("faceUrl"),
                    "plate_url": entry_session.get("plateUrl"),

                    # Exit session data
                    "exit_session_id": pair["exit_session_id"],
                    "exit_face_url": exit_session.get("faceUrl"),
                    "exit_plate_url": exit_session.get("plateUrl"),

                    # Verification data
                    "face_match_verified": pair["face_match_verified"],
                    "face_match_result": pair["face_match_result"]
                }

                grouped_sessions.append(grouped_session)
                used_session_ids.add(pair["entry_session_id"])
                used_session_ids.add(pair["exit_session_id"])

            # Add unpaired IN sessions (still parking)
            in_sessions = self._get_sessions_by_gate("In")
            for doc in in_sessions:
                if doc.id not in used_session_ids:
                    session_data = doc.to_dict()
                    entry_time = self._parse_timestamp(session_data.get("timestamp"))

                    plate_number = (session_data.get("plateNumber") or
                                  session_data.get("platenumber") or "Unknown")

                    grouped_session = {
                        "face_id": session_data.get("faceIndex", "Unknown"),
                        "license_plate": plate_number,
                        "entry_time": entry_time,
                        "exit_time": None,
                        "status": "active",  # Still parking
                        "duration": None,

                        # Entry session data
                        "entry_session_id": doc.id,
                        "face_url": session_data.get("faceUrl"),
                        "plate_url": session_data.get("plateUrl"),

                        # No exit data
                        "exit_session_id": None,
                        "exit_face_url": None,
                        "exit_plate_url": None,

                        # No verification data
                        "face_match_verified": False,
                        "face_match_result": None
                    }

                    grouped_sessions.append(grouped_session)
                    used_session_ids.add(doc.id)

            # Add unpaired OUT sessions (exit without entry OR invalid pair skipped above)
            out_sessions = self._get_sessions_by_gate("Out")
            for doc in out_sessions:
                if doc.id not in used_session_ids:
                    session_data = doc.to_dict()
                    exit_time = self._parse_timestamp(session_data.get("timestamp"))

                    plate_number = (session_data.get("plateNumber") or
                                  session_data.get("platenumber") or "Unknown")

                    grouped_session = {
                        "face_id": session_data.get("faceIndex", "Unknown"),
                        "license_plate": plate_number,
                        "entry_time": None,
                        "exit_time": exit_time,
                        "status": "failed",  # Exit without valid entry pairing
                        "duration": None,

                        # No entry data
                        "entry_session_id": None,
                        "face_url": None,
                        "plate_url": None,

                        # Exit session data
                        "exit_session_id": doc.id,
                        "exit_face_url": session_data.get("faceUrl"),
                        "exit_plate_url": session_data.get("plateUrl"),

                        # No (valid) verification data here
                        "face_match_verified": False,
                        "face_match_result": None
                    }

                    grouped_sessions.append(grouped_session)

            # Sort by most recent activity
            grouped_sessions.sort(key=lambda x: max(
                x["entry_time"] or datetime.min,
                x["exit_time"] or datetime.min
            ), reverse=True)

            return grouped_sessions

        except Exception as e:
            print(f"Error getting enhanced grouped sessions: {e}")
            return []

    def _get_all_sessions(self) -> List[Any]:
        """Get all sessions from Firestore"""
        collection_ref = get_collection(self.session_collection)
        return list(collection_ref.stream())

    def _get_sessions_by_gate(self, gate: str) -> List[Any]:
        """Get sessions by gate type"""
        collection_ref = get_collection(self.session_collection)
        query = collection_ref.where("gate", "==", gate)
        return list(query.stream())

    def _get_all_session_maps(self) -> List[Any]:
        """Get all session maps"""
        collection_ref = get_collection(self.session_map_collection)
        return list(collection_ref.stream())

    def _get_all_matching_verifications(self) -> List[Dict[str, Any]]:
        """Get all matching verifications"""
        try:
            collection_ref = get_collection(self.matching_verify_collection)
            docs = list(collection_ref.stream())
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Error getting matching verifications: {e}")
            return []

    def _find_verification_for_session(self, session_id: str, verifications: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find matching verification for a session"""
        for verification in verifications:
            if verification.get("sessionID") == session_id:
                return verification
        return None

    def _is_valid_session_pair(self, entry_session: Dict[str, Any], exit_session: Dict[str, Any], verification: Optional[Dict[str, Any]]) -> bool:
        """Check if a session pair is valid"""
        if not verification:
            return False
        if not verification.get("isMatch"):
            return False
        entry_time = self._parse_timestamp(entry_session.get("timestamp"))
        exit_time = self._parse_timestamp(exit_session.get("timestamp"))
        if entry_time and exit_time and entry_time >= exit_time:
            return False
        # Ensure plate and face indices align
        entry_plate = entry_session.get("plateNumber") or entry_session.get("platenumber")
        exit_plate = exit_session.get("plateNumber") or exit_session.get("platenumber")
        if entry_plate and exit_plate and entry_plate != exit_plate:
            return False
        entry_face = entry_session.get("faceIndex")
        exit_face = exit_session.get("faceIndex")
        if entry_face and exit_face and entry_face != exit_face:
            return False
        return True

    def _parse_timestamp(self, timestamp) -> Optional[datetime]:
        """Parse timestamp from various formats"""
        if not timestamp:
            return None

        try:
            if hasattr(timestamp, "isoformat"):
                return timestamp.replace(tzinfo=None)
            elif isinstance(timestamp, str):
                # Try parsing ISO format
                try:
                    return datetime.fromisoformat(timestamp.replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    return datetime.fromisoformat(timestamp)
            else:
                return datetime.fromisoformat(str(timestamp))
        except Exception as e:
            print(f"Error parsing timestamp {timestamp}: {e}")
            return None
