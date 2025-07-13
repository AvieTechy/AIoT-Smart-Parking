# Smart Parking Face Recognition API

## Quick Start

```bash
# Make startup script executable
chmod +x start.sh

# Start the API
./start.sh
```

## Project Structure

```
smart-parking/
├── start.sh              # Main startup script
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
├── backend/             # Core application
│   ├── api/             # FastAPI endpoints
│   │   ├── main.py      # Main API application
│   │   └── schemas.py   # Data validation schemas
│   ├── models/          # AI models
│   │   └── models/      # Model implementations
│   │       └── vggface2.py  # Face recognition model
│   ├── utils/           # Utility functions
│   │   ├── firebase.py  # Firestore database
│   │   └── cloudinary.py # Image storage
│   ├── config/          # Configuration
│   │   ├── settings.py  # App settings
│   │   ├── .env         # Environment variables
│   │   ├── .env.template # Environment template
│   │   └── firebase-key.json # Firebase credentials
└── docker/             # Container setup
    ├── Dockerfile      # Container definition
    └── docker-compose.yml # Service orchestration
```

## Configuration

### Environment Variables (.env)

```env
# API Security
API_KEY=smart-parking-api-key-2024

# Face Recognition
SIMILARITY_THRESHOLD=0.5

# Firebase (optional)
FIREBASE_PROJECT_ID=vispark-25
GOOGLE_APPLICATION_CREDENTIALS=firebase-key.json

# Cloudinary (required)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Firebase Setup (Optional)

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select project: `vispark-25`
3. Generate service account key
4. Save as `backend/config/firebase-key.json`

## API Endpoints

### Health Check
```http
GET /health
Headers: X-API-Key: smart-parking-api-key-2024
```

### Face Recognition
```http
POST /facematch
Headers:
  X-API-Key: smart-parking-api-key-2024
  Content-Type: application/json

Body:
{
  "person_id": "user123",
  "image_url": "https://example.com/face.jpg",
  "plate_number": "29A-12345",
  "gate": 0
}
```

## Development

### Prerequisites
- Docker Desktop
- 8GB+ RAM
- Internet connection

### Commands

```bash
# Start API
./start.sh

# Stop API
./start.sh stop

# Restart API
./start.sh restart

# View logs
./start.sh logs

# Build from scratch
cd docker && docker-compose up --build
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Security

- API key authentication required
- Firebase credentials secured
- Environment variables for sensitive data
- CORS protection enabled

## Features

- **Face Recognition**: VGGFace2 model with multiple backends
- **Real-time Processing**: Fast inference with OpenCV
- **Cloud Storage**: Cloudinary integration for images
- **Database**: Firebase Firestore for data persistence
- **API Documentation**: Auto-generated OpenAPI docs
- **Docker Support**: Containerized deployment

## Usage Flow

1. **Entry (Gate 0)**: Face registration/verification
2. **Exit (Gate 1)**: Face verification and billing
3. **Evidence Storage**: All images saved to Cloudinary
4. **Data Logging**: Entry/exit logs in Firebase

## Troubleshooting

### API not starting
```bash
# Check Docker
docker --version
docker info

# Check logs
./start.sh logs

# Rebuild
cd docker && docker-compose up --build
```

### Firebase connection failed
- Verify `firebase-key.json` exists
- Check Firebase project permissions
- Ensure project ID matches in .env

### Face recognition errors
- Verify image URL is accessible
- Check image format (JPG/PNG)
- Ensure face is clearly visible

## Support

- **Repository**: [AIoT-Smart-Parking](https://github.com/AvieTechy/AIoT-Smart-Parking)
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
