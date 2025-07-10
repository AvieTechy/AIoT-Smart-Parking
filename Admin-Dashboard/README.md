# Smart Parking Admin Dashboard

A comprehensive web-based admin dashboard for smart parking system management using **FastAPI + React (Vite + TypeScript)** with **Firestore** database.

## Features

### Authentication System
- Secure login/logout functionality
- Protected routes and session management
- Demo credentials: `admin` / `admin123`

### Real-time Dashboard
- Current vehicles count display
- Live statistics with interactive cards
- Responsive design for all devices

### Vehicle Management
- Complete entry/exit history tracking
- Vehicle information display (ID, Face, License plate, Time)
- Real-time status indicators (Parked/Exited)
- Duration tracking for parked vehicles

### Advanced Search & Filtering
- Search by license plate
- Date range filtering (from/to dates)
- Clear filters functionality
- Live search results

### Comprehensive Analytics
- Interactive charts (Bar & Line charts)
- Multiple time periods: Hour/Day/Week/Month/Year
- Entry vs Exit analytics
- Trend analysis with visual graphs

---

## Project Structure

```
admin-dashboard/
├── backend/                    # FastAPI server
│   ├── app/
│   │   ├── main.py            # FastAPI main application
│   │   ├── api/               # API routes
│   │   ├── core/              # Core configurations
│   │   ├── db/                # Database connections
│   │   ├── models/            # Data models
│   │   └── services/          # Business logic
│   ├── firebase_key.json     # Firebase credentials
│   └── requirements.txt      # Python dependencies
├── frontend/                  # React frontend (Vite)
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── styles/            # Modular CSS files
│   │   ├── types/             # TypeScript definitions
│   │   ├── App.tsx            # Main App component
│   │   └── main.tsx           # Entry point
│   ├── package.json           # Frontend dependencies
│   └── vite.config.ts         # Vite configuration
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

---

## Getting Started

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.8 or higher)
- Firebase account and project

### Backend Setup (FastAPI)

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate         # On Windows
# source .venv/bin/activate    # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure Firebase:
   - Place your `firebase_key.json` in the backend directory
   - Update Firebase configuration in `app/core/config.py`

5. Start the server:
```bash
uvicorn app.main:app --reload
```

Server will run at: **http://localhost:8000**

### Frontend Setup (React + Vite)

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will run at: **http://localhost:5173**

---

## 🛠️ Technologies Used

### Backend
- **FastAPI** - Modern, fast web framework for Python
- **Firebase Firestore** - NoSQL cloud database
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server implementation

### Frontend
- **React 19** - JavaScript library for building user interfaces
- **TypeScript** - Typed superset of JavaScript
- **Vite** - Fast build tool and development server
- **React Router** - Declarative routing for React
- **Recharts** - Composable charting library
- **Lucide React** - Beautiful & consistent icon toolkit
- **date-fns** - Modern JavaScript date utility library

### Styling
- **CSS Modules** - Modular and reusable CSS
- **Responsive Design** - Mobile-first approach
- **Modern UI** - Clean and professional interface

---

## Screenshots

### Login Page
- Secure authentication with gradient background
- Form validation and error handling

### Dashboard Overview
- Real-time statistics cards
- Vehicle count and occupancy rate
- Tab-based navigation

### Vehicle History
- Comprehensive data table
- Face recognition integration
- Status badges and duration tracking

### Analytics
- Interactive charts and graphs
- Multiple time period analysis
- Trend visualization

---

## Development

### Available Scripts

#### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

#### Backend
- `uvicorn app.main:app --reload` - Start development server
- `python -m pytest` - Run tests (if available)

### API Endpoints

- `GET /api/users` - Get all users
- `POST /api/users` - Create new user
- `GET /api/vehicles` - Get vehicle history
- `POST /api/vehicles` - Add new vehicle entry

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request