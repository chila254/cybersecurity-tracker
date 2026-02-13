'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { apiClient } from './api-client'

interface User {
  id: string
  email: string
  name: string
  role: 'ADMIN' | 'ANALYST' | 'VIEWER'
  org_id: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (orgName: string, email: string, password: string, name: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token')
    const userData = localStorage.getItem('user')
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData))
      } catch (error) {
        console.error('Failed to parse user data:', error)
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      }
    }
    
    setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const { data, error } = await apiClient.post('/auth/login', { email, password })
    
    if (error) throw new Error(error)
    
    const token = (data as any).access_token
    apiClient.setToken(token)
    
    // Decode JWT to get user info (simple decode, not validation)
    const parts = token.split('.')
    if (parts.length === 3) {
      const payload = JSON.parse(atob(parts[1]))
      const userData = {
        id: payload.sub,
        email: payload.email,
        name: payload.email.split('@')[0],
        role: payload.role,
        org_id: payload.org_id,
      }
      setUser(userData)
      localStorage.setItem('user', JSON.stringify(userData))
    }
  }

  const register = async (orgName: string, email: string, password: string, name: string) => {
    const { data, error } = await apiClient.post('/auth/register', {
      org_name: orgName,
      user_data: {
        email,
        password,
        name,
        role: 'ADMIN',
      },
    })
    
    if (error) throw new Error(error)
    
    const token = (data as any).access_token
    apiClient.setToken(token)
    
    // Decode JWT to get user info
    const parts = token.split('.')
    if (parts.length === 3) {
      const payload = JSON.parse(atob(parts[1]))
      const userData = {
        id: payload.sub,
        email: payload.email,
        name,
        role: payload.role,
        org_id: payload.org_id,
      }
      setUser(userData)
      localStorage.setItem('user', JSON.stringify(userData))
    }
  }

  const logout = () => {
    setUser(null)
    apiClient.clearToken()
    localStorage.removeItem('user')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
