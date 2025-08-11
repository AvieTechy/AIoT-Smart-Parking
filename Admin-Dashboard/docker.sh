#!/bin/bash

# Smart Parking Admin Dashboard - Docker Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to build images
build_images() {
    print_status "Building Docker images..."

    # Build backend
    print_status "Building backend image..."
    docker build -t smart-parking-backend:latest ./backend

    # Build frontend
    print_status "Building frontend image..."
    docker build -t smart-parking-frontend:latest ./frontend

    # Build development frontend
    print_status "Building development frontend image..."
    docker build -f ./frontend/Dockerfile.dev -t smart-parking-frontend-dev:latest ./frontend

    print_success "All images built successfully"
}

# Function to start services
start_services() {
    print_status "Starting Smart Parking Admin Dashboard..."

    if [ "$1" == "dev" ]; then
        print_status "Starting in development mode with hot reload..."
        docker-compose --profile development up -d
    else
        print_status "Starting in production mode..."
        docker-compose up -d backend frontend
    fi

    print_success "Services started successfully"
    print_status "Backend API: http://localhost:8000"
    print_status "Frontend Dashboard: http://localhost:3000"

    if [ "$1" == "dev" ]; then
        print_status "Development Frontend: http://localhost:5174"
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping Smart Parking Admin Dashboard..."
    docker-compose down
    print_success "Services stopped successfully"
}

# Function to view logs
view_logs() {
    if [ -z "$1" ]; then
        print_status "Showing logs for all services..."
        docker-compose logs -f
    else
        print_status "Showing logs for $1..."
        docker-compose logs -f $1
    fi
}

# Function to restart services
restart_services() {
    print_status "Restarting Smart Parking Admin Dashboard..."
    stop_services
    start_services $1
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."

    # Stop and remove containers
    docker-compose down --volumes --remove-orphans

    # Remove images
    docker rmi smart-parking-backend:latest smart-parking-frontend:latest smart-parking-frontend-dev:latest 2>/dev/null || true

    # Remove unused volumes and networks
    docker volume prune -f
    docker network prune -f

    print_success "Cleanup completed"
}

# Function to show status
show_status() {
    print_status "Smart Parking Admin Dashboard Status:"
    docker-compose ps

    print_status "\nResource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Function to check health
check_health() {
    print_status "Checking service health..."

    # Check backend health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend API is healthy"
    else
        print_error "Backend API is not responding"
    fi

    # Check frontend health
    if curl -f http://localhost:3000/health >/dev/null 2>&1; then
        print_success "Frontend is healthy"
    else
        print_error "Frontend is not responding"
    fi
}

# Function to show usage
show_usage() {
    echo "Smart Parking Admin Dashboard - Docker Management"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build          Build Docker images"
    echo "  start [dev]    Start services (add 'dev' for development mode)"
    echo "  stop           Stop all services"
    echo "  restart [dev]  Restart services"
    echo "  logs [service] View logs (optionally for specific service)"
    echo "  status         Show service status and resource usage"
    echo "  health         Check service health"
    echo "  cleanup        Remove all containers, images, and volumes"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start in production mode"
    echo "  $0 start dev      # Start in development mode"
    echo "  $0 logs backend   # View backend logs"
    echo "  $0 restart dev    # Restart in development mode"
}

# Main script logic
case "${1:-}" in
    build)
        check_docker
        build_images
        ;;
    start)
        check_docker
        start_services "$2"
        ;;
    stop)
        check_docker
        stop_services
        ;;
    restart)
        check_docker
        restart_services "$2"
        ;;
    logs)
        check_docker
        view_logs "$2"
        ;;
    status)
        check_docker
        show_status
        ;;
    health)
        check_health
        ;;
    cleanup)
        check_docker
        cleanup
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        echo ""
        show_usage
        exit 1
        ;;
esac
