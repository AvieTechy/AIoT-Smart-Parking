"""
Script để tạo dữ liệu mẫu cho Firestore
Chạy script này để tạo dữ liệu test cho hệ thống parking
"""

import os
import sys
import json
from datetime import datetime, timedelta
import uuid
import firebase_admin
from firebase_admin import credentials, firestore

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        # Đường dẫn tới file firebase key
        key_path = os.path.join(os.path.dirname(__file__), 'firebase_key.json')
        if not os.path.exists(key_path):
            print(f"Error: Firebase key file not found at {key_path}")
            print("Please make sure firebase_key.json exists in the backend directory")
            return None
        
        try:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            return None
    
    return firestore.client()

def create_sample_sessions(db):
    """Tạo dữ liệu mẫu cho Sessions"""
    print("Creating sample sessions...")
    
    # Dữ liệu mẫu cho các session
    sample_sessions = [
        # Vehicle 1 - Đã vào và ra
        {
            "session_id": str(uuid.uuid4()),
            "plateUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/plate_01.jpg",
            "faceUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/face_01.jpg",
            "gate": "In",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "isOut": True,  # Đã checkout
            "faceIndex": "face_001",
            "plateNumber": "30A-12345"
        },
        {
            "session_id": str(uuid.uuid4()),
            "plateUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/plate_01_out.jpg",
            "faceUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/face_01_out.jpg",
            "gate": "Out",
            "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "isOut": False,
            "faceIndex": "face_001",
            "plateNumber": "30A-12345"
        },
        
        # Vehicle 2 - Chỉ vào, chưa ra (đang trong bãi)
        {
            "session_id": str(uuid.uuid4()),
            "plateUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/plate_02.jpg",
            "faceUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/face_02.jpg",
            "gate": "In",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "isOut": False,  # Chưa checkout
            "faceIndex": "face_002",
            "plateNumber": "29B-67890"
        },
        
        # Vehicle 3 - Chỉ vào, chưa ra (đang trong bãi)
        {
            "session_id": str(uuid.uuid4()),
            "plateUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/plate_03.jpg",
            "faceUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/face_03.jpg",
            "gate": "In",
            "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat(),
            "isOut": False,  # Chưa checkout
            "faceIndex": "face_003",
            "plateNumber": "51C-11111"
        },
        
        # Vehicle 4 - Đã vào và ra hoàn thành
        {
            "session_id": str(uuid.uuid4()),
            "plateUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/plate_04.jpg",
            "faceUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/face_04.jpg",
            "gate": "In",
            "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
            "isOut": True,  # Đã checkout
            "faceIndex": "face_004",
            "plateNumber": "77D-22222"
        },
        {
            "session_id": str(uuid.uuid4()),
            "plateUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/plate_04_out.jpg",
            "faceUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/face_04_out.jpg",
            "gate": "Out",
            "timestamp": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
            "isOut": False,
            "faceIndex": "face_004",
            "plateNumber": "77D-22222"
        },
        
        # Vehicle 5 - Mới vào (very recent)
        {
            "session_id": str(uuid.uuid4()),
            "plateUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/plate_05.jpg",
            "faceUrl": "https://res.cloudinary.com/demo/image/upload/v1234567890/face_05.jpg",
            "gate": "In",
            "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
            "isOut": False,  # Chưa checkout
            "faceIndex": "face_005",
            "plateNumber": "92E-33333"
        }
    ]
    
    # Lưu sessions vào Firestore
    sessions_ref = db.collection('Session')
    plate_map_ref = db.collection('PlateMap')
    
    for session_data in sample_sessions:
        session_id = session_data.pop('session_id')
        
        # Lưu session
        sessions_ref.document(session_id).set(session_data)
        
        # Tạo plate mapping
        plate_map_ref.document(session_data['plateNumber']).set({
            'sessionID': session_id
        })
        
        print(f"Created session {session_id}: {session_data['plateNumber']} - {session_data['gate']}")
    
    print(f"Created {len(sample_sessions)} sample sessions")

def create_sample_parking_slots(db):
    """Tạo dữ liệu mẫu cho ParkingSlots"""
    print("Creating sample parking slots...")
    
    slots_ref = db.collection('ParkingSlot')
    
    # Tạo 20 slot parking từ A1 đến D5
    rows = ['A', 'B', 'C', 'D']
    cols = range(1, 6)  # 1 to 5
    
    slot_count = 0
    for row in rows:
        for col in cols:
            slot_id = str(uuid.uuid4())
            location_code = f"{row}{col}"
            
            # Random một số slot đã occupied (tỷ lệ ~30%)
            is_occupied = slot_count % 3 == 0  # Every 3rd slot is occupied
            
            slot_data = {
                'location_code': location_code,
                'is_occupied': is_occupied,
                'updated_at': datetime.now()
            }
            
            slots_ref.document(slot_id).set(slot_data)
            print(f"Created parking slot {location_code}: {'Occupied' if is_occupied else 'Available'}")
            slot_count += 1
    
    print(f"Created {slot_count} parking slots")

def main():
    """Main function để chạy script"""
    print("=== Creating Sample Data for Firestore ===")
    
    # Initialize Firebase
    db = initialize_firebase()
    if not db:
        return
    
    try:
        # Tạo dữ liệu mẫu
        create_sample_sessions(db)
        print()
        create_sample_parking_slots(db)
        
        print("\n=== Sample Data Creation Completed ===")
        print("You can now start the backend server and test the APIs!")
        
        # In ra một số thông tin hữu ích
        print("\nSample data created:")
        print("- 7 Sessions (2 vehicles still in parking, 2 completed trips, 1 recent entry)")
        print("- 20 Parking slots (A1-D5, ~30% occupied)")
        print("\nTest URLs after starting server:")
        print("- GET http://localhost:8000/api/sessions/grouped")
        print("- GET http://localhost:8000/api/sessions/current-vehicle-count")
        print("- GET http://localhost:8000/api/parking/stats")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")

if __name__ == "__main__":
    main()
