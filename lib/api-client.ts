/**
 * API Client for communicating with FastAPI backend
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  'https://cybersecurity-tracker.onrender.com/api'

interface ApiError {
  detail?: any
  error?: string
  status_code?: number
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl

    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token')
    }
  }

  setToken(token: string) {
    this.token = token
    localStorage.setItem('access_token', token)
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('access_token')
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    return headers
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<{ data?: T; error?: string }> {
    const url = `${this.baseUrl}${endpoint}`

    console.log('[API Request]', url)

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...(options.headers || {}),
        },
        mode: 'cors',
        credentials: 'include',
      })

      if (response.status === 401) {
        this.clearToken()
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
      }

      const data = await response.json()
      console.log('[API Response]', data)

      if (!response.ok) {
        let errorMessage = 'An error occurred'

        if (Array.isArray(data.detail)) {
          errorMessage = data.detail.map((d: any) => d.msg).join(', ')
        } else if (data.detail) {
          errorMessage = data.detail
        } else if (data.error) {
          errorMessage = data.error
        } else {
          errorMessage = JSON.stringify(data)
        }

        console.error('[API Error]', errorMessage)
        return { error: errorMessage }
      }

      return { data: data as T }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Network error'

      console.error('[API Exception]', errorMessage)
      return { error: errorMessage }
    }
  }

  async get<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T>(endpoint: string, body?: unknown) {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async put<T>(endpoint: string, body?: unknown) {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async delete<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

export const apiClient = new ApiClient()
