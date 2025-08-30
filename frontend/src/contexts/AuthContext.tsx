import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User as AuthUser } from '@supabase/supabase-js';
import { User } from '../types';
import { supabase } from '../lib/supabase';
import apiService from '../services/api';
import toast from 'react-hot-toast';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1) 应用启动：同步当前 session 的 access_token
    (async () => {
      const { data } = await supabase.auth.getSession();
      const t = data.session?.access_token;
      if (t) {
        apiService.setToken(t);
        try {
          const userData = await apiService.getCurrentUser();
          setUser(userData);
        } catch (e) {
          console.error('Bootstrap getCurrentUser failed:', e);
        }
      }
      setLoading(false);
    })();

    // 2) 监听会话变化：TOKEN_REFRESHED/SIGNED_IN/SIGNED_OUT，同步 ApiService token
    const { data: sub } = supabase.auth.onAuthStateChange(async (event, session) => {
      const t = session?.access_token;
      if (t) {
        apiService.setToken(t);
        // TOKEN_REFRESHED 时通常无需每次都请求用户，但为稳妥可按需刷新
        try {
          const userData = await apiService.getCurrentUser();
          setUser(userData);
        } catch (e) {
          console.error('onAuthStateChange getCurrentUser failed:', e);
        }
      } else {
        apiService.clearToken();
        setUser(null);
      }
    });

    return () => {
      sub.subscription.unsubscribe();
    };
  }, []);

  const handleAuthSession = async (session: any) => {
    try {
      // Set the access token for API calls
      apiService.setToken(session.access_token);
      
      // Get user data from our API
      const userData = await apiService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to get user data:', error);
    }
  };

  const checkAuth = async () => {
    try {
      const { data } = await supabase.auth.getSession();
      const t = data.session?.access_token;
      if (t) {
        apiService.setToken(t);
        const userData = await apiService.getCurrentUser();
        setUser(userData);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      apiService.clearToken();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      
      // Login via Supabase Auth (client-side), then use access_token for backend calls
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
      if (!data.session) throw new Error('No session returned from Supabase');
      
      const accessToken = data.session.access_token;
      apiService.setToken(accessToken);
      
      // Ensure token is applied before calling backend
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const userData = await apiService.getCurrentUser();
      setUser(userData);
      
      toast.success('Login successful!');
    } catch (error: any) {
      console.error('Login failed:', error);
      const message = error?.message || error?.response?.data?.detail || 'Login failed';
      toast.error(message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, username: string, password: string, fullName?: string) => {
    try {
      setLoading(true);
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            username: username,
            full_name: fullName,
          },
        },
      });

      if (error) {
        throw error;
      }

      if (data.user) {
        if (data.user.email_confirmed_at) {
          // Auto-login if email is confirmed
          await login(email, password);
        } else {
          toast.success('Registration successful! Please check your email for verification.');
        }
      }
    } catch (error: any) {
      console.error('Registration failed:', error);
      toast.error(error.message || 'Registration failed');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await supabase.auth.signOut();
      apiService.clearToken();
      setUser(null);
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const refreshUser = async () => {
    try {
      const userData = await apiService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};