import React, { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import authService, { type User } from '../services/authService'

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  isAuthenticated: boolean
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in and verify token
    const initAuth = async () => {
      try {
        const storedUser = authService.getUser()
        if (storedUser && authService.getToken()) {
          // Verify token is still valid
          const verifiedUser = await authService.verifyToken()
          if (verifiedUser) {
            setUser(verifiedUser)
          } else {
            // Token is invalid, clear auth
            authService.logout()
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error)
        authService.logout()
      } finally {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [])

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const userData = await authService.login(username, password)
      setUser(userData)
      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  const logout = () => {
    authService.logout()
    setUser(null)
  }

  const value: AuthContextType = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    isLoading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
