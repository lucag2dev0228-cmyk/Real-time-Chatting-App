import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

// Define types
interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (userData: RegisterData) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  updateUser: (userData: User) => void;
  isAuthenticated: boolean;
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

interface AuthProviderProps {
  children: ReactNode;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(true);

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async (): Promise<void> => {
      if (token) {
        try {
          const response = await axios.get('/api/auth/profile/');
          setUser(response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          logout();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await axios.post('/api/auth/login/', {
        email,
        password,
      });

      const { user: userData, token: authToken } = response.data;
      
      setUser(userData);
      setToken(authToken);
      localStorage.setItem('token', authToken);
      
      axios.defaults.headers.common['Authorization'] = `Token ${authToken}`;
      
      toast.success('Login successful!');
      return { success: true };
    } catch (error: any) {
      const message = error.response?.data?.error || 'Login failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const register = async (userData: RegisterData): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await axios.post('/api/auth/register/', userData);

      console.log(response.data);
      const { user: newUser, token: authToken } = response.data;
      
      setUser(newUser);
      setToken(authToken);
      localStorage.setItem('token', authToken);
      
      axios.defaults.headers.common['Authorization'] = `Token ${authToken}`;
      
      toast.success('Registration successful!');
      return { success: true };
    } catch (error: any) {
      const message = error.response?.data?.error || 'Registration failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = async (): Promise<void> => {
    try {
      if (token) {
        await axios.post('/api/auth/logout/');
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      toast.success('Logged out successfully');
    }
  };

  const updateUser = (userData: User): void => {
    setUser(userData);
  };

  const value: AuthContextType = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

