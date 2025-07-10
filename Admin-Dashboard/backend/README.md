# Smart Parking Admin Backend

Backend API for Smart Parking Admin System using FastAPI and Firebase/Firestore.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing project
3. Enable Firestore Database
4. Go to Project Settings > Service Accounts
5. Click "Generate new private key" 
6. Download the JSON file and rename it to `firebase_key.json`
7. Place `firebase_key.json` in the `backend/` directory

### 3. Environment Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update the `.env` file with your configuration if needed.

### 4. Run the Application

```bash
# From the backend directory
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

API Documentation will be available at: `http://localhost:8000/docs`

## Firestore Collections Structure

The application uses the following Firestore collections based on the new workflow:

### 1. Session Collection
- **Document ID**: sessionID (UUID)
- **Fields**: 
  - plateUrl (string): URL ảnh biển số (Cloudinary)
  - faceUrl (string): URL ảnh khuôn mặt (Cloudinary)  
  - timestamp (string): Timestamp as string
  - gate (string): "In" hoặc "Out"
  - isOut (boolean): false khi mới tạo
  - faceIndex (string): Face index (null for In sessions initially, copied from In session for Out sessions)
  - plateNumber (string): Plate number (null initially for In sessions, detected later)
  - faceEmbedding (array): Face embedding vector (null initially, extracted later)

### 2. IsNewSession Collection  
- **Document ID**: statusDoc
- **Fields**: 
  - status (boolean): true nếu đang có session mới
  - sessionID (string): session hiện tại

### 3. MatchingVerify Collection
- **Document ID**: Auto-generated UUID
- **Fields**: 
  - sessionID (string): Session ID của lượt ra
  - isMatch (boolean): Kết quả so khớp face

### 4. SessionMap Collection
- **Document ID**: Auto-generated UUID
- **Fields**: 
  - entrySessionID (string): Session ID lúc vào
  - exitSessionID (string): Session ID lúc ra

### 5. PlateMap Collection
- **Document ID**: License plate number (e.g., "AB-1234")
- **Fields**: 
  - sessionID (string): ID của session tương ứng lượt vào

### 6. ParkingSlot Collection
- **Document ID**: Auto-generated UUID
- **Fields**: locationCode, isOccupied, updatedAt

## API Endpoints

### Session Management
- `POST /api/sessions/` - Create new session (basic creation without AI processing)
- `POST /api/sessions/out` - Create exit session with entry session data
- `POST /api/sessions/process-entry` - Process entry session (AI: plate detection + face embedding)
- `POST /api/sessions/process-exit` - Process exit session (AI: plate detection + face matching)
- `GET /api/sessions/{session_id}` - Get session by ID
- `GET /api/sessions/` - Get all sessions (with filters)
- `PATCH /api/sessions/{session_id}/out` - Mark session as out
- `GET /api/sessions/plate/{plate_number}/session` - Get session by plate number
- `POST /api/sessions/matching-verify` - Create matching verification result
- `POST /api/sessions/session-map` - Create session mapping (entry-exit)
- `POST /api/sessions/update-session` - Update session fields
- `GET /api/sessions/new-session-status` - Get new session status
- `POST /api/sessions/clear-new-session-status` - Clear new session status

### Processing Workflows
- `POST /api/processing/entry-flow` - Complete entry workflow (create session + AI processing)
- `POST /api/processing/exit-flow` - Complete exit workflow (create session + AI processing)
- `GET /api/processing/session/{session_id}/processing-status` - Check processing status
- `GET /api/processing/plate/{plate_number}/matching-history` - Get matching history

### Parking Management
- `POST /api/parking/slots` - Create parking slot
- `GET /api/parking/slots` - Get all parking slots
- `GET /api/parking/slots/available` - Get available slots
- `PATCH /api/parking/slots/{slot_id}` - Update slot occupancy
- `GET /api/parking/stats` - Get parking statistics

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health check including Firebase connection

## Usage Examples

### Entry Flow (Device -> Firebase -> AI Processing)
```bash
# Step 1: Device creates basic session
curl -X POST "http://localhost:8000/api/sessions/" \
  -H "Content-Type: application/json" \
  -d '{
    "plateUrl": "https://cloudinary.com/plate.jpg",
    "faceUrl": "https://cloudinary.com/face.jpg", 
    "gate": "In",
    "faceIndex": "abc123"
  }'

# Step 2: Server processes AI tasks (plate detection + face embedding)
curl -X POST "http://localhost:8000/api/sessions/process-entry?session_id=SESSION_ID"
```

### Alternative: Complete Entry Flow (One Call)
```bash
curl -X POST "http://localhost:8000/api/processing/entry-flow" \
  -H "Content-Type: application/json" \
  -d '{
    "plateUrl": "https://cloudinary.com/plate.jpg",
    "faceUrl": "https://cloudinary.com/face.jpg", 
    "gate": "In",
    "faceIndex": "abc123"
  }'
```

### Exit Flow (Device -> Firebase -> AI Processing)
```bash
# Step 1: Device creates exit session with entry session data
curl -X POST "http://localhost:8000/api/sessions/out" \
  -H "Content-Type: application/json" \
  -d '{
    "plateUrl": "https://cloudinary.com/plate_out.jpg",
    "faceUrl": "https://cloudinary.com/face_out.jpg",
    "faceIndex": "abc123",
    "plateNumber": "AB-1234"
  }'

# Step 2: Server processes AI tasks (plate detection + face matching)
curl -X POST "http://localhost:8000/api/sessions/process-exit?session_id=SESSION_ID"
```

### Alternative: Complete Exit Flow (One Call)
```bash
curl -X POST "http://localhost:8000/api/processing/exit-flow" \
  -H "Content-Type: application/json" \
  -d '{
    "plateUrl": "https://cloudinary.com/plate_out.jpg",
    "faceUrl": "https://cloudinary.com/face_out.jpg",
    "faceIndex": "abc123",
    "plateNumber": "AB-1234"
  }'
```

### Check Processing Status
```bash
curl "http://localhost:8000/api/processing/session/SESSION_ID/processing-status"
```

### Get Parking Statistics
```bash
curl "http://localhost:8000/api/parking/stats"
```

## Workflow Documentation

### Entry Workflow (Luồng vào)

1. **Device -> Firebase**: Create Session with basic data
   ```
   Session {
     ID: str (UUID)
     plateUrl: str (Cloudinary URL)
     faceUrl: str (Cloudinary URL)
     timestamp: str
     gate: "In"
     isOut: false
     faceIndex: str
     plateNumber: null (will be detected)
     faceEmbedding: null (will be extracted)
   }
   ```

2. **Server AI Processing**:
   - `plate_number_detection(plateUrl)` → detect plate number
   - `face_recognition(faceUrl)` → extract face embedding
   - Update session: `plateNumber = detected_plate`, `faceEmbedding = extracted_embedding`
   - Create PlateMap: `plateMap[plateNumber] = sessionID`

3. **Result**: Entry session ready with plate number and face embedding

### Exit Workflow (Luồng ra)

1. **Device -> Firebase**: Create Session with entry session data
   ```
   Session {
     ID: str (UUID)
     plateUrl: str (Cloudinary URL)
     faceUrl: str (Cloudinary URL)
     timestamp: str
     gate: "Out"
     isOut: false
     faceIndex: str (from In session)
     plateNumber: str (from In session)
     faceEmbedding: null (will be extracted)
   }
   ```

2. **Server AI Processing**:
   - `plate_number_detection(plateUrl)` → verify plate number
   - `face_recognition(faceUrl)` → extract exit face embedding
   - Find entry session: `sessionID = plateMap[plateNumber]`
   - Face matching: `isMatch = faceMatching(entry_embedding, exit_embedding)`
   - Create MatchingVerify: `{sessionID: exit_session_id, isMatch: bool}`
   - If match: Create SessionMap: `{entrySessionID, exitSessionID}`

3. **Result**: Exit processed with matching verification

## Notes

- Make sure your Firebase project has Firestore enabled
- The Firebase service account key must have Firestore read/write permissions
- Collections will be created automatically when first accessed
- The API includes CORS support for frontend integration
