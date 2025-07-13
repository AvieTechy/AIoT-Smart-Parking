#!/bin/bash

# Smart Parking Face Recognition API - Startup Script
# Author: AvieTechy
# Version: 1.0

set -e

echo "Smart Parking API - Starting..."

# Function to check if command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "$1 is not installed. Please install $1 first."
        exit 1
    fi
}

# Function to check Docker status
check_docker() {
    if ! docker info &> /dev/null; then
        echo "Starting Docker..."
        open -a Docker
        echo "Waiting for Docker to start..."
        while ! docker info &> /dev/null; do
            sleep 2
        done
    fi
    echo "Docker is running"
}

# Function to setup environment
setup_env() {
    if [ ! -f "backend/config/.env" ]; then
        echo ".env file not found. Creating from template..."
        cp backend/config/.env.template backend/config/.env
        echo "Please edit backend/config/.env with your API keys"
        return 1
    fi
    echo "Environment configured"
}

# Function to check Firebase key
check_firebase() {
    if [ ! -f "backend/config/firebase-key.json" ]; then
        echo "Firebase key not found"
        echo "Please add your firebase-key.json to backend/config/"
        return 1
    fi
    echo "Firebase key found"
}

# Main execution
main() {
    echo "Checking prerequisites..."

    # Check required commands
    check_command docker
    check_command docker-compose

    # Check Docker
    check_docker

    # Setup environment
    if ! setup_env; then
        exit 1
    fi

    # Check Firebase
    if ! check_firebase; then
        echo "Continuing without Firebase (mock mode)"
    fi

    echo ""
    echo "Starting Smart Parking API..."
    cd docker
    docker-compose up -d

    echo ""
    echo "Waiting for API to start..."
    sleep 10

    # Test API
    if curl -s -H "X-API-Key: smart-parking-api-key-2024" http://localhost:8000/health &> /dev/null; then
        echo "API is running successfully!"
        echo ""
        echo "Access URLs:"
        echo "   API: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
        echo ""
        echo "API Key: smart-parking-api-key-2024"
    else
        echo "API failed to start. Check logs with:"
        echo "   docker-compose logs smart-parking-api"
    fi
}

# Handle script arguments
case "${1:-}" in
    stop)
        echo "Stopping Smart Parking API..."
        cd docker && docker-compose down
        ;;
    restart)
        echo "Restarting Smart Parking API..."
        cd docker && docker-compose restart
        ;;
    logs)
        cd docker && docker-compose logs -f smart-parking-api
        ;;
    *)
        main
        ;;
esac
