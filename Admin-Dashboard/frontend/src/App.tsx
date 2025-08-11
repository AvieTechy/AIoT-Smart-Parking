import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ParkingProvider } from './contexts/ParkingContext'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import ParkingMap from './components/ParkingMap'
import StatisticsPage from './components/StatisticsPage'
import SettingsPage from './components/SettingsPage'
import ProtectedRoute from './components/ProtectedRoute.tsx'
import Layout from './components/Layout'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <ParkingProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Dashboard />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/parking-map"
                element={
                <ProtectedRoute>
                  <Layout>
                    <ParkingMap />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <Layout>
                    <StatisticsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Layout>
                    <SettingsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
      </ParkingProvider>
    </AuthProvider>
  )
}

export default App
