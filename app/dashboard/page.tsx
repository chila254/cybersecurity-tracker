'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { StatsCard } from '@/components/dashboard/stats-card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { AlertTriangle, Clock, AlertCircle, Shield, CheckCircle, TrendingUp } from 'lucide-react'

interface DashboardData {
  stats: {
    total_incidents: number
    open_incidents: number
    critical_severity: number
    total_vulnerabilities: number
    unpatched_vulnerabilities: number
    incidents_this_month: number
  }
  incident_trends: Array<{ date: string; count: number }>
  severity_distribution: Array<{ severity: string; count: number }>
}

interface Incident {
  id: string
  title: string
  severity: string
  status: string
  created_at: string
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Fetch dashboard stats
        const { data: dashData } = await apiClient.get<DashboardData>('/dashboard')
        if (dashData) {
          setData(dashData)
        }

        // Fetch recent incidents
        const { data: incidentData } = await apiClient.get<Incident[]>('/incidents?limit=5')
        if (incidentData) {
          setIncidents(incidentData)
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-slate-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'text-red-400 bg-red-900/20'
      case 'HIGH':
        return 'text-orange-400 bg-orange-900/20'
      case 'MEDIUM':
        return 'text-yellow-400 bg-yellow-900/20'
      case 'LOW':
        return 'text-blue-400 bg-blue-900/20'
      default:
        return 'text-slate-400 bg-slate-900/20'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OPEN':
        return 'bg-red-900/20 text-red-300'
      case 'INVESTIGATING':
        return 'bg-yellow-900/20 text-yellow-300'
      case 'RESOLVED':
        return 'bg-green-900/20 text-green-300'
      case 'CLOSED':
        return 'bg-slate-700/20 text-slate-300'
      default:
        return 'bg-slate-700/20 text-slate-300'
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Security Dashboard</h1>
        <p className="text-slate-400">Real-time incident and vulnerability monitoring</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm font-medium">Total Incidents</span>
            <AlertTriangle className="w-5 h-5 text-red-400" />
          </div>
          <p className="text-3xl font-bold text-white">{data?.stats.total_incidents || 0}</p>
        </div>

        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm font-medium">Open Incidents</span>
            <Clock className="w-5 h-5 text-orange-400" />
          </div>
          <p className="text-3xl font-bold text-white">{data?.stats.open_incidents || 0}</p>
          <p className="text-xs text-orange-400 mt-2">{data?.stats.incidents_this_month || 0} this month</p>
        </div>

        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm font-medium">Critical Issues</span>
            <AlertCircle className="w-5 h-5 text-red-500" />
          </div>
          <p className="text-3xl font-bold text-white">{data?.stats.critical_severity || 0}</p>
        </div>

        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm font-medium">Total Vulnerabilities</span>
            <Shield className="w-5 h-5 text-yellow-400" />
          </div>
          <p className="text-3xl font-bold text-white">{data?.stats.total_vulnerabilities || 0}</p>
        </div>

        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm font-medium">Unpatched Vulns</span>
            <TrendingUp className="w-5 h-5 text-orange-400" />
          </div>
          <p className="text-3xl font-bold text-white">{data?.stats.unpatched_vulnerabilities || 0}</p>
        </div>

        <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm font-medium">Patch Coverage</span>
            <CheckCircle className="w-5 h-5 text-green-400" />
          </div>
          <div className="flex items-end gap-2">
            <p className="text-3xl font-bold text-green-400">
              {data?.stats.total_vulnerabilities
                ? Math.round(
                    ((data.stats.total_vulnerabilities - (data.stats.unpatched_vulnerabilities || 0)) /
                      data.stats.total_vulnerabilities) *
                      100
                  )
                : 0}
              %
            </p>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2 mt-3">
            <div
              className="bg-green-500 h-2 rounded-full"
              style={{
                width: `${data?.stats.total_vulnerabilities ? Math.round(((data.stats.total_vulnerabilities - (data.stats.unpatched_vulnerabilities || 0)) / data.stats.total_vulnerabilities) * 100) : 0}%`
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* Recent Incidents */}
      <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-white">Recent Incidents</h2>
            <p className="text-slate-400 text-sm">Latest security incidents</p>
          </div>
          <Link href="/incidents">
            <Button className="bg-red-600 hover:bg-red-700 text-white">View All</Button>
          </Link>
        </div>

        {incidents.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-slate-400">No incidents recorded yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {incidents.map((incident) => (
              <div
                key={incident.id}
                className="flex items-center justify-between p-4 bg-slate-800 rounded-lg hover:bg-slate-700/50 transition-colors"
              >
                <div className="flex-1">
                  <p className="text-white font-medium">{incident.title}</p>
                  <p className="text-slate-400 text-sm">
                    {new Date(incident.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getSeverityColor(incident.severity)}`}>
                    {incident.severity}
                  </span>
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(incident.status)}`}>
                    {incident.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
