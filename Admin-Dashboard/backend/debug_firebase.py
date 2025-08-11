"""
Script to check Firebase data structure and debug the counting issues
"""
import firebase_admin
from firebase_admin import credentials, firestore
import json

def check_firebase_data():
    try:
        # Initialize Firebase (if not already done)
        try:
            firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate('firebase_key.json')
            firebase_admin.initialize_app(cred)

        db = firestore.client()

        print("=== Checking Firebase Collections ===")

        # Check Session collection
        sessions_ref = db.collection('Session')
        sessions = list(sessions_ref.limit(5).stream())

        print(f"\nSession collection has {len(list(sessions_ref.stream()))} documents")
        print("Sample Session documents:")
        for doc in sessions:
            data = doc.to_dict()
            print(f"  ID: {doc.id}")
            print(f"  Data: {json.dumps(data, indent=2, default=str)}")
            print("  ---")

        # Check ParkingSlot collection
        parking_ref = db.collection('ParkingSlot')
        parking_docs = list(parking_ref.limit(3).stream())

        print(f"\nParkingSlot collection has {len(list(parking_ref.stream()))} documents")
        print("Sample ParkingSlot documents:")
        for doc in parking_docs:
            data = doc.to_dict()
            print(f"  ID: {doc.id}")
            print(f"  Data: {json.dumps(data, indent=2, default=str)}")
            print("  ---")

        # Check other collections mentioned in the image
        for collection_name in ['ParkingMeta', 'slotCounter']:
            try:
                coll_ref = db.collection(collection_name)
                docs = list(coll_ref.limit(3).stream())
                print(f"\n{collection_name} collection has {len(list(coll_ref.stream()))} documents")
                if docs:
                    print("Sample documents:")
                    for doc in docs:
                        data = doc.to_dict()
                        print(f"  ID: {doc.id}")
                        print(f"  Data: {json.dumps(data, indent=2, default=str)}")
                        print("  ---")
            except Exception as e:
                print(f"Error accessing {collection_name}: {e}")

        # Count current vehicles using correct logic
        print("\n=== Analyzing Vehicle Count Logic ===")

        # Method 1: Count In sessions where isOut = False
        in_sessions_active = sessions_ref.where('gate', '==', 'In').where('isOut', '==', False).stream()
        count_method1 = len(list(in_sessions_active))
        print(f"Method 1 - In sessions with isOut=False: {count_method1}")

        # Method 2: Count all In sessions
        all_in_sessions = sessions_ref.where('gate', '==', 'In').stream()
        count_all_in = len(list(all_in_sessions))
        print(f"Method 2 - All In sessions: {count_all_in}")

        # Method 3: Count all Out sessions
        all_out_sessions = sessions_ref.where('gate', '==', 'Out').stream()
        count_all_out = len(list(all_out_sessions))
        print(f"Method 3 - All Out sessions: {count_all_out}")

        # Method 4: Calculate difference
        current_vehicles_calc = count_all_in - count_all_out
        print(f"Method 4 - Calculated (In - Out): {current_vehicles_calc}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_firebase_data()
