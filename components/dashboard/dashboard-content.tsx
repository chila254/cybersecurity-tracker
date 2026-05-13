'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { StatsCard } from '@/components/dashboard/stats-card'
import { RecentIncidents } from '@/components/dashboard/recent-incidents'
import { SecurityOverview } from '@/components/dashboard/security-overview'
import { NetworkStatus } from '@/components/dashboard/network-status'
import {
  AlertTriangle,
  Clock,
  AlertCircle,
  Shield,
  CheckCircle,
  TrendingUp,
  Activity,
  Zap
} from 'lucide-react'

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

export function DashboardContent() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const { data: dashData } = await apiClient.get<DashboardData>('/dashboard')
        if (dashData) {
          setData(dashData)
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
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500"></div>
      </div>
    )
  }

  const stats = data?.stats || {
    total_incidents: 0,
    open_incidents: 0,
    critical_severity: 0,
    total_vulnerabilities: 0,
    unpatched_vulnerabilities: 0,
    incidents_this_month: 0
  }

  return (
    <div className="flex-1 overflow-auto">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Security Dashboard</h1>
            <p className="text-slate-400 text-sm">Real-time incident and vulnerability monitoring</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-2 bg-green-900/20 rounded-lg border border-green-700/50">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-400 text-sm font-medium">All Systems Operational</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="p-6 space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total Incidents"
            value={stats.total_incidents}
            icon={AlertTriangle}
            color="red"
            trend="+12%"
            description="vs last month"
          />
          <StatsCard
            title="Open Incidents"
            value={stats.open_incidents}
            icon={Clock}
            color="orange"
            trend="+8%"
            description={`${stats.incidents_this_month} this month`}
          />
          <StatsCard
            title="Critical Issues"
            value={stats.critical_severity}
            icon={AlertCircle}
            color="red"
            trend="-5%"
            description="immediate attention"
          />
          <StatsCard
            title="System Health"
            value="98.5%"
            icon={Activity}
            color="green"
            trend="+2%"
            description="uptime this month"
          />
        </div>

        {/* Vulnerability Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <StatsCard
            title="Total Vulnerabilities"
            value={stats.total_vulnerabilities}
            icon={Shield}
            color="yellow"
            trend="+3%"
            description="active CVEs"
          />
          <StatsCard
            title="Unpatched Vulns"
            value={stats.unpatched_vulnerabilities}
            icon={TrendingUp}
            color="orange"
            trend="-2%"
            description="need attention"
          />
          <StatsCard
            title="Patch Coverage"
            value={`${stats.total_vulnerabilities ? Math.round(((stats.total_vulnerabilities - stats.unpatched_vulnerabilities) / stats.total_vulnerabilities) * 100) : 0}%`}
            icon={CheckCircle}
            color="green"
            trend="+5%"
            description="patched systems"
          />
        </div>

        {/* Charts and Recent Activity */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Security Overview Chart */}
          <div className="xl:col-span-2">
            <div className="bg-slate-900 rounded-xl border border-slate-700 p-6">
              <h2 className="text-lg font-bold text-white mb-4">Security Overview</h2>
              <p className="text-slate-400">Chart components temporarily disabled</p>
            </div>
          </div>

          {/* Network Status */}
          <div className="space-y-6">
            <NetworkStatus />
            <RecentIncidents />
          </div>
        </div>
      </div>
    </div>
  )
}