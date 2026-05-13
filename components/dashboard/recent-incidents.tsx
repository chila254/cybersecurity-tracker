'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { Clock, AlertTriangle, CheckCircle, User } from 'lucide-react'

interface Incident {
  id: string
  title: string
  severity: string
  status: string
  created_at: string
  assignee?: string
}

export function RecentIncidents() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const { data } = await apiClient.get<Incident[]>('/incidents?limit=5')
        if (data) {
          setIncidents(data)
        }
      } catch (error) {
        console.error('Failed to fetch incidents:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchIncidents()
  }, [])

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/30'
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30'
      case 'MEDIUM':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'LOW':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'OPEN':
      case 'INVESTIGATING':
        return <Clock className="w-4 h-4 text-orange-400" />
      case 'RESOLVED':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      default:
        return <AlertTriangle className="w-4 h-4 text-slate-400" />
    }
  }

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-white">Recent Incidents</h2>
          <p className="text-slate-400 text-sm">Latest security events</p>
        </div>
        <Link href="/incidents">
          <Button variant="outline" size="sm" className="border-slate-600 text-slate-300 hover:text-white">
            View All
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-16 bg-slate-800 rounded-lg"></div>
            </div>
          ))}
        </div>
      ) : incidents.length === 0 ? (
        <div className="text-center py-8">
          <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-3" />
          <p className="text-slate-400 text-sm">No active incidents</p>
        </div>
      ) : (
        <div className="space-y-3">
          {incidents.map((incident) => (
            <div
              key={incident.id}
              className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:bg-slate-800 transition-colors cursor-pointer"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium text-sm truncate mb-1">
                    {incident.title}
                  </p>
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    {getStatusIcon(incident.status)}
                    <span>{new Date(incident.created_at).toLocaleDateString()}</span>
                    {incident.assignee && (
                      <>
                        <span>•</span>
                        <div className="flex items-center gap-1">
                          <User className="w-3 h-3" />
                          <span>{incident.assignee}</span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(incident.severity)}`}>
                  {incident.severity}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}