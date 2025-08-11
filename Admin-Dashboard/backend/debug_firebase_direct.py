from app.db.firestore import get_collection

def debug_firebase_direct():
    """Debug Firebase direct access to check plateNumber fields"""
    try:
        collection_ref = get_collection("Session")

        # Get a few specific sessions
        specific_sessions = ["sess_113776", "sess_10601"]

        print("=== DIRECT FIREBASE CHECK ===")
        for session_id in specific_sessions:
            doc_ref = collection_ref.document(session_id)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                print(f"\nSession: {session_id}")
                print(f"Gate: {data.get('gate', 'N/A')}")
                print(f"Raw plateNumber: {repr(data.get('plateNumber', 'MISSING'))}")
                print(f"Raw platenumber: {repr(data.get('platenumber', 'MISSING'))} (lowercase)")
                print(f"All fields: {list(data.keys())}")

                # Look for any field that might contain plate number
                for key, value in data.items():
                    if 'plate' in key.lower():
                        print(f"  Found plate field: {key} = {repr(value)}")
            else:
                print(f"\nSession {session_id}: NOT FOUND")

        # Sample a few more sessions
        print(f"\n=== SAMPLE OF ALL SESSIONS ===")
        query = collection_ref.limit(10)
        docs = query.stream()

        for doc in docs:
            data = doc.to_dict()
            plate_fields = {}
            for key, value in data.items():
                if 'plate' in key.lower() and value:
                    plate_fields[key] = value

            if plate_fields:
                print(f"Session {doc.id}: {plate_fields}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_firebase_direct()
