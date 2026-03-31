import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../api/auth';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) { setLoading(false); return; }
    try {
      // decode the JWT payload for quick user info
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUser({ 
        id: payload.user_id, 
        username: payload.username || payload.name || 'User', 
        email: payload.email,
        user_type: payload.user_type
      });
    } catch {
      localStorage.clear();
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadUser(); }, [loadUser]);

  const login = async (credentials) => {
    const res = await authAPI.login(credentials);
    const { access, refresh } = res.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    api.defaults.headers.common.Authorization = `Bearer ${access}`;
    const payload = JSON.parse(atob(access.split('.')[1]));
    const userData = { 
      id: payload.user_id, 
      username: payload.username || 'User', 
      email: payload.email,
      user_type: payload.user_type
    };
    setUser(userData);
    return userData;
  };

  const register = async (data) => {
    const res = await authAPI.register(data);
    const { access, refresh } = res.data;
    if (access && refresh) {
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      api.defaults.headers.common.Authorization = `Bearer ${access}`;
      const payload = JSON.parse(atob(access.split('.')[1]));
      const userData = { 
        id: payload.user_id, 
        username: payload.username || 'User', 
        email: payload.email,
        user_type: payload.user_type
      };
      setUser(userData);
      return userData;
    }
    return res.data;
  };

  const logout = async () => {
    const refresh = localStorage.getItem('refresh_token');
    try { if (refresh) await authAPI.logout(refresh); } catch {}
    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};
