'use client'

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import api from './api'

// Types
export interface User {
  id: string
  email: string
  username: string
  first_name: string
  last_name: string
  role: 'admin' | 'manager' | 'user'
  is_verified: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
}

interface RegisterData {
  email: string
  username: string
  password: string
  password_confirm: string
  first_name?: string
  last_name?: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  })
  const router = useRouter()

  // Fetch current user on mount
  const fetchCurrentUser = useCallback(async () => {
    try {
      const response = await api.get('/auth/me/')
      setState({
        user: response.data.user,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error) {
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      })
    }
  }, [])

  useEffect(() => {
    fetchCurrentUser()
  }, [fetchCurrentUser])

  // Login function
  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email, password })
    
    if (response.data.success) {
      setState({
        user: response.data.user,
        isAuthenticated: true,
        isLoading: false,
      })
      router.push('/dashboard')
    }
  }

  // Register function
  const register = async (data: RegisterData) => {
    const response = await api.post('/auth/register/', data)
    
    if (response.data.success) {
      setState({
        user: response.data.user,
        isAuthenticated: true,
        isLoading: false,
      })
      router.push('/dashboard')
    }
  }

  // Logout function
  const logout = async () => {
    try {
      await api.post('/auth/logout/')
    } catch (error) {
      // Ignore errors
    }
    
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    })
    router.push('/login')
  }

  // Refresh token function
  const refreshToken = async () => {
    try {
      await api.post('/auth/token/refresh/')
    } catch (error) {
      // If refresh fails, logout
      logout()
    }
  }

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        refreshToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// Custom hook to use auth
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
