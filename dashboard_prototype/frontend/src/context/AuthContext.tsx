import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { AuthUser } from '../types';
import * as api from '../services/api';

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Global Authentication Provider.
 * Centralizes user state, token management, and auth actions.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize state from storage on mount
  useEffect(() => {
    const initAuth = () => {
      const storedToken = api.getAuthToken();
      const storedUser = localStorage.getItem('rpa_user');
      
      if (storedToken && storedUser) {
        try {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
        } catch (e) {
          console.error('Failed to parse stored user session:', e);
          api.logout(); // Clear potentially corrupt data
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await api.login(username, password);
      setUser(response.user);
      setToken(response.access_token);
      localStorage.setItem('rpa_user', JSON.stringify(response.user));
    } catch (error) {
      console.error('Login attempt failed:', error);
      throw error;
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
    setToken(null);
    localStorage.removeItem('rpa_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to access auth context values.
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
