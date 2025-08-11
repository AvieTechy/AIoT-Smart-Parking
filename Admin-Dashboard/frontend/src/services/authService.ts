const API_BASE_URL = 'http://localhost:8000';

export interface User {
  user_id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

class AuthService {
  private baseURL = API_BASE_URL;
  private tokenKey = 'access_token';
  private userKey = 'user';

  // Get stored token
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  // Get stored user
  getUser(): User | null {
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = this.getToken();
    const user = this.getUser();
    return !!(token && user);
  }

  // Store token and user
  private storeAuth(token: string, user: User): void {
    localStorage.setItem(this.tokenKey, token);
    localStorage.setItem(this.userKey, JSON.stringify(user));
  }

  // Clear stored auth data
  private clearAuth(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  // Get authorization headers
  private getAuthHeaders(): HeadersInit {
    const token = this.getToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  // Login
  async login(username: string, password: string): Promise<User> {
    try {
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Login failed');
      }

      const data: LoginResponse = await response.json();
      this.storeAuth(data.access_token, data.user);
      return data.user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  // Register
  async register(userData: RegisterRequest): Promise<User> {
    try {
      const response = await fetch(`${this.baseURL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Registration failed');
      }

      const user: User = await response.json();
      return user;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  // Logout
  async logout(): Promise<void> {
    try {
      const token = this.getToken();
      if (token) {
        await fetch(`${this.baseURL}/auth/logout`, {
          method: 'POST',
          headers: this.getAuthHeaders(),
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearAuth();
    }
  }

  // Verify token
  async verifyToken(): Promise<User | null> {
    try {
      const token = this.getToken();
      if (!token) {
        return null;
      }

      const response = await fetch(`${this.baseURL}/auth/verify`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        this.clearAuth();
        return null;
      }

      const data = await response.json();
      return data.user;
    } catch (error) {
      console.error('Token verification error:', error);
      this.clearAuth();
      return null;
    }
  }

  // Get current user info
  async getCurrentUser(): Promise<User> {
    try {
      const response = await fetch(`${this.baseURL}/auth/me`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Failed to get user info');
      }

      const user: User = await response.json();
      // Update stored user data
      localStorage.setItem(this.userKey, JSON.stringify(user));
      return user;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  }

  // Refresh token
  async refreshToken(): Promise<string> {
    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Token refresh failed');
      }

      const data = await response.json();
      localStorage.setItem(this.tokenKey, data.access_token);
      return data.access_token;
    } catch (error) {
      console.error('Token refresh error:', error);
      this.clearAuth();
      throw error;
    }
  }

  // Make authenticated request
  async authenticatedRequest(url: string, options: RequestInit = {}): Promise<Response> {
    const headers = {
      ...this.getAuthHeaders(),
      ...options.headers,
    };

    let response = await fetch(url, {
      ...options,
      headers,
    });

    // If token expired, try to refresh
    if (response.status === 401) {
      try {
        await this.refreshToken();
        // Retry with new token
        response = await fetch(url, {
          ...options,
          headers: {
            ...this.getAuthHeaders(),
            ...options.headers,
          },
        });
      } catch {
        this.clearAuth();
        throw new Error('Session expired. Please login again.');
      }
    }

    return response;
  }
}

export const authService = new AuthService();
export default authService;
