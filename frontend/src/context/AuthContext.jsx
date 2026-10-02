import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(() => {
        const saved = localStorage.getItem('truthlens_user');
        try {
            return saved ? JSON.parse(saved) : null;
        } catch {
            return null;
        }
    });
    const [token, setToken] = useState(() => localStorage.getItem('truthlens_token') || null);
    const [isLoading, setIsLoading] = useState(true);

    const logout = useCallback(async () => {
        try {
            if (token) await api.logout();
        } catch {
            // Ignore failure on logout call
        } finally {
            localStorage.removeItem('truthlens_token');
            localStorage.removeItem('truthlens_user');
            setToken(null);
            setUser(null);
        }
    }, [token]);

    useEffect(() => {
        const checkAuth = async () => {
            if (token) {
                try {
                    const userData = await api.getMe();
                    setUser(userData);
                    localStorage.setItem('truthlens_user', JSON.stringify(userData));
                } catch {
                    logout();
                }
            }
            setIsLoading(false);
        };
        checkAuth();
    }, [token, logout]);

    const login = async (credentials) => {
        const res = await api.login(credentials);
        localStorage.setItem('truthlens_token', res.token);
        localStorage.setItem('truthlens_user', JSON.stringify(res.user));
        setToken(res.token);
        setUser(res.user);
        return res;
    };

    return (
        <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, isLoading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
