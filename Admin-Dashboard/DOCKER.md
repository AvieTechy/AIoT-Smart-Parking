# Smart Parking Admin Dashboard - Docker Setup

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git (for cloning the repository)

### 1. Build and Start (Production Mode)
```bash
# Build Docker images
./docker.sh build

# Start services in production mode
./docker.sh start

# Access the application
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
```

### 2. Development Mode (with Hot Reload)
```bash
# Start services in development mode
./docker.sh start dev

# Access the application
# - Frontend (Production): http://localhost:3000
# - Frontend (Development): http://localhost:5174
# - Backend API: http://localhost:8000
```

## Docker Management Commands

### Basic Commands
```bash
# Build all Docker images
./docker.sh build

# Start services
./docker.sh start          # Production mode
./docker.sh start dev      # Development mode

# Stop services
./docker.sh stop

# Restart services
./docker.sh restart        # Production mode
./docker.sh restart dev    # Development mode
```

### Monitoring Commands
```bash
# View logs for all services
./docker.sh logs

# View logs for specific service
./docker.sh logs backend
./docker.sh logs frontend

# Check service status and resource usage
./docker.sh status

# Check service health
./docker.sh health
```

### Maintenance Commands
```bash
# Clean up all Docker resources
./docker.sh cleanup

# Show help
./docker.sh help
```

## Service Architecture

### Backend (Port 8000)
- **Image**: `smart-parking-backend:latest`
- **Framework**: FastAPI with Python 3.9
- **Database**: Firebase Firestore
- **Features**:
  - Enhanced session pairing with face matching verification
  - Real-time dashboard statistics
  - RESTful API with automatic documentation

### Frontend (Port 3000/5174)
- **Production Image**: `smart-parking-frontend:latest` (Nginx)
- **Development Image**: `smart-parking-frontend-dev:latest` (Vite dev server)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Features**:
  - Real-time dashboard with auto-refresh
  - Enhanced session management with verification status
  - Responsive UI with modern design

## Environment Configuration

### Backend Environment Variables
```bash
PYTHONPATH=/app
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
```

### Frontend Environment Variables
```bash
# Production
REACT_APP_API_URL=http://localhost:8000

# Development
VITE_API_URL=http://localhost:8000
```

## Volume Mounts

### Development Mode
- `./backend:/app` - Backend code with hot reload
- `./frontend:/app` - Frontend code with hot reload
- `./backend/logs:/app/logs` - Backend logs persistence

### Production Mode
- `./backend/logs:/app/logs` - Backend logs persistence only

## Network Configuration

All services run on the `smart-parking-network` bridge network for internal communication.

### Port Mappings
- **3000** → Frontend (Production)
- **5174** → Frontend (Development)
- **8000** → Backend API

## Health Checks

Both services include health checks:
- **Backend**: `GET /health` endpoint
- **Frontend**: Nginx status check

Health checks run every 30 seconds with 3 retries.

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   lsof -i :3000

   # Stop conflicting services
   ./docker.sh stop
   ```

2. **Docker Not Running**
   ```bash
   # Start Docker Desktop
   # Then verify
   docker info
   ```

3. **Build Failures**
   ```bash
   # Clean and rebuild
   ./docker.sh cleanup
   ./docker.sh build
   ```

4. **Service Not Responding**
   ```bash
   # Check service status
   ./docker.sh status

   # Check logs
   ./docker.sh logs backend
   ./docker.sh logs frontend

   # Check health
   ./docker.sh health
   ```

### Debug Mode

To run with more verbose logging:
```bash
# View live logs while services are running
./docker.sh logs

# Or for specific service
./docker.sh logs backend
```

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - Code changes are automatically reflected (volume mount)
   - Restart not required for most changes

2. **Frontend Changes**:
   - Use development mode: `./docker.sh start dev`
   - Hot reload enabled on port 5174
   - Production build on port 3000

### Adding Dependencies

1. **Backend**:
   ```bash
   # Stop services
   ./docker.sh stop

   # Add dependency to requirements.txt
   # Rebuild image
   ./docker.sh build

   # Restart
   ./docker.sh start
   ```

2. **Frontend**:
   ```bash
   # For development mode, exec into container
   docker exec -it smart-parking-frontend-dev npm install <package>

   # For production, update package.json and rebuild
   ./docker.sh build
   ```

## Production Deployment

### Environment Preparation
1. Update environment variables for production
2. Configure proper CORS origins
3. Set up SSL certificates (if needed)
4. Configure proper logging levels

### Deployment Commands
```bash
# Production deployment
./docker.sh build
./docker.sh start

# Monitor deployment
./docker.sh status
./docker.sh health
```

## Security Considerations

1. **API Security**: CORS configured for development origins
2. **Nginx Security**: Security headers enabled
3. **Container Security**: Non-root user in containers
4. **Network Security**: Internal network for service communication

## Performance Optimization

1. **Multi-stage builds** for smaller production images
2. **Nginx gzip compression** for frontend assets
3. **Static asset caching** with appropriate headers
4. **Health checks** for reliable service monitoring
