import React, { createContext, useContext, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
// FIX: The path is now corrected to point to the right file.
import { getCurrentUser, User } from '../api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const { data, isLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
        try {
            const response = await getCurrentUser();
            return response.data;
        } catch (error) {
            return null; // On error (like 401), treat as not logged in
        }
    },
    retry: false, // Don't retry on auth errors
    refetchOnWindowFocus: true, // Re-check auth when user returns to the tab
  });

  const user = data?.authenticated ? data.user : null;
  const isAuthenticated = !!user;

  const value = {
    user: user || null,
    isAuthenticated,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

