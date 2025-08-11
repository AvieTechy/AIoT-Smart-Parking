# Smart Parking Admin Dashboard Makefile
# Environment: aiot conda environment

.PHONY: help install-backend install-frontend install dev dev-backend dev-frontend build-frontend clean stop

# Default target
help:
	@echo "Smart Parking Admin Dashboard Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install          - Install all dependencies (backend + frontend)"
	@echo "  install-backend  - Install backend dependencies"
	@echo "  install-frontend - Install frontend dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  dev              - Run both backend and frontend in development mode"
	@echo "  dev-backend      - Run only backend server"
	@echo "  dev-frontend     - Run only frontend server"
	@echo ""
	@echo "Build Commands:"
	@echo "  build-frontend   - Build frontend for production"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean            - Clean node_modules and Python cache"
	@echo "  stop             - Stop all running servers"
	@echo ""

# Install all dependencies
install: install-backend install-frontend
	@echo "✅ All dependencies installed successfully!"

# Install backend dependencies
install-backend:
	@echo "🐍 Installing backend dependencies..."
	cd backend && conda run -n aiot pip install -r requirements.txt
	@echo "✅ Backend dependencies installed!"

# Install frontend dependencies
install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed!"

# Run both backend and frontend in development mode
dev:
	@echo "🚀 Starting both backend and frontend servers..."
	@echo "Backend will run on: http://localhost:8000"
	@echo "Frontend will run on: http://localhost:5173"
	@echo "Press Ctrl+C to stop both servers"
	@make dev-backend & make dev-frontend; \
	wait

# Run only backend server
dev-backend:
	@echo "🐍 Starting FastAPI backend server..."
	@echo "Server will run on: http://localhost:8000"
	@echo "API docs available at: http://localhost:8000/docs"
	cd backend && conda run -n aiot uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run only frontend server
dev-frontend:
	@echo "⚛️ Starting React frontend server..."
	@echo "Server will run on: http://localhost:5173"
	cd frontend && ./node_modules/.bin/vite

# Build frontend for production
build-frontend:
	@echo "🏗️ Building frontend for production..."
	cd frontend && ./node_modules/.bin/vite build
	@echo "✅ Frontend built successfully!"

# Clean dependencies and cache
clean:
	@echo "🧹 Cleaning up..."
	@echo "Removing node_modules..."
	rm -rf frontend/node_modules
	@echo "Removing Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# Stop all running servers
stop:
	@echo "🛑 Stopping all servers..."
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@pkill -f "npm run dev" 2>/dev/null || true
	@echo "✅ All servers stopped!"

# Development shortcuts
backend: dev-backend
frontend: dev-frontend
start: dev
build: build-frontend
