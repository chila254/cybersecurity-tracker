'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function ApiCheckPage() {
  const [apiUrl, setApiUrl] = useState<string>('')
  const [testResults, setTestResults] = useState<{
    url: string
    status: string
    responseTime: number
    error?: string
  }[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
    setApiUrl(url)
  }, [])

  const testEndpoint = async (endpoint: string) => {
    setLoading(true)
    const fullUrl = `${apiUrl}${endpoint}`
    const startTime = Date.now()

    try {
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          organization_name: 'Test Org',
          email: 'test@example.com',
          password: 'TestPassword123',
          name: 'Test User',
        }),
      })

      const responseTime = Date.now() - startTime
      const data = await response.json()

      setTestResults((prev) => [
        ...prev,
        {
          url: fullUrl,
          status: `${response.status} ${response.statusText}`,
          responseTime,
          error: response.ok
            ? undefined
            : data.detail || data.error || 'Unknown error',
        },
      ])
    } catch (error) {
      const responseTime = Date.now() - startTime
      setTestResults((prev) => [
        ...prev,
        {
          url: fullUrl,
          status: 'NETWORK ERROR',
          responseTime,
          error: error instanceof Error ? error.message : 'Unknown error',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const clearResults = () => {
    setTestResults([])
  }

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">API Connection Diagnostic</h1>

        {/* API URL Display */}
        <div className="bg-slate-800 rounded-lg p-6 mb-6 border border-slate-700">
          <h2 className="text-lg font-semibold text-white mb-2">Current API URL</h2>
          <div className="bg-slate-900 p-4 rounded border border-slate-600 mb-4">
            <code className="text-green-400 text-sm break-all">{apiUrl}</code>
          </div>

          {!apiUrl || apiUrl === 'http://localhost:8000/api' ? (
            <div className="p-4 bg-red-900/20 border border-red-700/50 rounded text-red-300 text-sm">
              ⚠️ WARNING: API_URL is not set or using localhost! You need to set NEXT_PUBLIC_API_URL in your Vercel environment variables to:
              <br />
              <code className="block mt-2 font-mono">https://cybersecurity-tracker.onrender.com/api</code>
            </div>
          ) : (
            <div className="p-4 bg-green-900/20 border border-green-700/50 rounded text-green-300 text-sm">
              ✓ API URL is configured
            </div>
          )}
        </div>

        {/* Test Buttons */}
        <div className="bg-slate-800 rounded-lg p-6 mb-6 border border-slate-700">
          <h2 className="text-lg font-semibold text-white mb-4">Test Endpoints</h2>
          <div className="flex gap-3 flex-wrap">
            <Button
              onClick={() => testEndpoint('/auth/register')}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              Test Register
            </Button>
            <Button onClick={clearResults} disabled={loading} className="bg-slate-700 hover:bg-slate-600 text-white">
              Clear Results
            </Button>
          </div>
        </div>

        {/* Test Results */}
        {testResults.length > 0 && (
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-lg font-semibold text-white mb-4">Test Results</h2>
            <div className="space-y-4">
              {testResults.map((result, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded border ${
                    result.status.includes('NETWORK ERROR')
                      ? 'bg-red-900/20 border-red-700/50'
                      : result.status.startsWith('2')
                      ? 'bg-green-900/20 border-green-700/50'
                      : 'bg-yellow-900/20 border-yellow-700/50'
                  }`}
                >
                  <div className="mb-2">
                    <p className="text-white font-mono text-sm break-all">{result.url}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-slate-400">Status:</p>
                      <p className="text-white font-mono">{result.status}</p>
                    </div>
                    <div>
                      <p className="text-slate-400">Response Time:</p>
                      <p className="text-white font-mono">{result.responseTime}ms</p>
                    </div>
                  </div>
                  {result.error && (
                    <div className="mt-2">
                      <p className="text-slate-400 text-sm">Error:</p>
                      <p className="text-red-300 text-sm font-mono break-all">{result.error}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Troubleshooting Guide */}
        <div className="bg-slate-800 rounded-lg p-6 mt-6 border border-slate-700">
          <h2 className="text-lg font-semibold text-white mb-4">Troubleshooting Guide</h2>
          <div className="space-y-4 text-slate-300 text-sm">
            <div>
              <p className="font-semibold text-white mb-2">1. NETWORK ERROR</p>
              <p>
                This means the frontend can't reach the backend. Check:
              </p>
              <ul className="list-disc ml-5 mt-2 space-y-1">
                <li>NEXT_PUBLIC_API_URL is set correctly in Vercel</li>
                <li>Backend is running at https://cybersecurity-tracker.onrender.com</li>
                <li>No CORS errors (check backend CORS configuration)</li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-white mb-2">2. Status 422 (Validation Error)</p>
              <p>The request format is wrong. Backend expects specific field names.</p>
            </div>
            <div>
              <p className="font-semibold text-white mb-2">3. Status 500 (Server Error)</p>
              <p>Backend error. Check backend logs on Render console.</p>
            </div>
            <div>
              <p className="font-semibold text-white mb-2">4. CORS Error</p>
              <p>
                Backend needs to allow your Vercel domain. Check backend CORS settings to include:
              </p>
              <code className="block mt-2 bg-slate-900 p-2 rounded">
                https://v0-cybersecurity-tracker-dashboard-opal.vercel.app
              </code>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
