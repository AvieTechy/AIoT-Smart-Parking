# Smart Parking Admin Dashboard - Setup Guide

## 🔥 Firebase Setup Requirements

### 1. Firebase Project Setup
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project or use existing one
3. Enable **Firestore Database** in the project
4. Go to **Project Settings** > **Service Accounts**
5. Click **Generate new private key**
6. Download the JSON file and rename it to `firebase_key.json`
7. Place `firebase_key.json` in the `backend/` directory

### 2. Database Structure
The dashboard expects these Firestore collections:

```
/Session                    # Main vehicle sessions
├── {sessionId}
│   ├── plateUrl: string   # Cloudinary URL for plate image
│   ├── faceUrl: string    # Cloudinary URL for face image
│   ├── timestamp: string  # ISO timestamp
│   ├── gate: "In" | "Out" # Entry or exit gate
│   ├── isOut: boolean     # false for entry, true for exit
│   ├── faceIndex: string  # Face recognition index
│   └── plateNumber: string # License plate number

/PlateMap                   # Maps plate numbers to sessions
├── {plateNumber}
│   └── sessionID: string

/SessionMap                 # Links entry and exit sessions
├── {mapId}
│   ├── entrySessionID: string
│   └── exitSessionID: string

/MatchingVerify            # Face matching results
├── {verifyId}
│   ├── sessionID: string
│   └── isMatch: boolean

/ParkingSlot               # Parking space management
├── {slotId}
│   ├── location_code: string  # e.g., "A1", "B2"
│   ├── is_occupied: boolean
│   └── updated_at: timestamp

/IsNewSession              # Status tracking
└── statusDoc
    ├── status: boolean
    └── sessionID: string
```

## 🚀 Quick Start

### Step 1: Setup Firebase
```bash
# Place your firebase_key.json in backend directory
cp /path/to/your/firebase_key.json backend/firebase_key.json
```

### Step 2: Install Dependencies
```bash
# Install all dependencies (backend + frontend)
make install
```

### Step 3: Create Sample Data
```bash
# Create sample sessions and admin user
cd backend
conda run -n aiot python create_sample_data.py
conda run -n aiot python create_admin_user.py
```

### Step 4: Start Servers
```bash
# Start both backend and frontend
make dev

# Or start them separately:
make dev-backend   # Backend: http://localhost:8000
make dev-frontend  # Frontend: http://localhost:5173
```

### Step 5: Access Dashboard
1. Open browser and go to: http://localhost:5173
2. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`

## 🔧 Configuration

### Environment Variables
Backend uses `.env` file in `backend/` directory:

```env
# Firebase Configuration
FIREBASE_KEY_PATH=firebase_key.json

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-please
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Configuration
Frontend automatically connects to backend at `http://localhost:8000`.

To change this, edit `src/services/authService.ts` and `src/services/apiService.ts`:
```typescript
const API_BASE_URL = 'http://your-backend-url:port';
```

## 🔍 Testing the Setup

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "firebase": "connected",
  "timestamp": "2025-08-01T00:00:00Z"
}
```

### 2. API Documentation
Visit: http://localhost:8000/docs

### 3. Check Database Schema
```bash
curl http://localhost:8000/api/schema
```

## 📊 Sample Data

The `create_sample_data.py` script creates:
- 10 sample parking sessions (entry/exit pairs)
- 5 parking slots with different occupancy states
- Realistic timestamps and vehicle data
- Face matching verification records

## 🛠️ Available Commands

### Makefile Commands
```bash
make install          # Install all dependencies
make dev              # Run both servers
make dev-backend      # Run backend only
make dev-frontend     # Run frontend only
make build-frontend   # Build for production
make clean            # Clean cache and node_modules
make stop             # Stop all servers
make help             # Show all commands
```

### Backend Scripts
```bash
# Create admin user (username: admin, password: admin123)
conda run -n aiot python create_admin_user.py

# Create sample data for testing
conda run -n aiot python create_sample_data.py

# Start backend manually
conda run -n aiot uvicorn app.main:app --reload
```

### Frontend Scripts
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🐛 Troubleshooting

### Firebase Connection Issues
1. Check `firebase_key.json` is in correct location
2. Verify Firebase project has Firestore enabled
3. Check service account permissions
4. Test with health endpoint: `curl http://localhost:8000/health`

### Frontend Issues
1. If `vite` command conflicts, Makefile uses direct path: `./node_modules/.bin/vite`
2. Check console for CORS errors
3. Verify backend is running on port 8000

### Backend Issues
1. Check conda environment `aiot` is activated
2. Verify all Python dependencies are installed
3. Check `.env` file configuration
4. Look at server logs for detailed errors

## 📝 Default Credentials

After running `create_admin_user.py`:
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Change default password after first login!

## 🔐 Security Notes

1. Change JWT secret key in production
2. Use strong admin password
3. Configure proper CORS origins
4. Secure Firebase service account key
5. Use HTTPS in production

## 📚 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user
- `GET /auth/verify` - Verify token

### Sessions
- `GET /api/sessions` - Get all sessions
- `GET /api/sessions/{id}` - Get specific session
- `POST /api/sessions` - Create new session

### Parking
- `GET /api/parking/slots` - Get all parking slots
- `GET /api/parking/stats` - Get parking statistics
- `PATCH /api/parking/slots/{id}` - Update slot occupancy

### Utilities
- `GET /health` - Health check with Firebase status
- `GET /api/schema` - Database schema documentation
