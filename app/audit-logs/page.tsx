'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'

interface AuditLog {
  id: string
  timestamp: string
  user_id: string
  action: string
  resource_type: string
  resource_id: string
  old_values?: any
  new_values?: any
  ip_address?: string
  user_agent?: string
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<any>(null)
  
  // Filters
  const [actionFilter, setActionFilter] = useState('')
  const [resourceFilter, setResourceFilter] = useState('')
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(20)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    fetchLogs()
    fetchStats()
  }, [actionFilter, resourceFilter, page])

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (actionFilter) params.append('action', actionFilter)
      if (resourceFilter) params.append('resource_type', resourceFilter)
      params.append('skip', (page * pageSize).toString())
      params.append('limit', pageSize.toString())
      
      let url = '/audit-logs'
      if (params.toString()) url += '?' + params.toString()

      const { data } = await apiClient.get(url)
      setLogs(data.logs || [])
      setTotal(data.total || 0)
    } catch (error) {
      console.error('Failed to fetch audit logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const { data } = await apiClient.get('/audit-logs/stats')
      setStats(data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'CREATE':
        return 'bg-green-900/20 text-green-300'
      case 'UPDATE':
        return 'bg-blue-900/20 text-blue-300'
      case 'DELETE':
        return 'bg-red-900/20 text-red-300'
      default:
        return 'bg-slate-700/20 text-slate-300'
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Audit Logs</h1>
        <p className="text-slate-400">Complete change history for compliance and investigation</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-400 text-sm">Total Logs</p>
            <p className="text-2xl font-bold text-white">{stats.total_logs}</p>
          </div>
          <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-400 text-sm">Active Users</p>
            <p className="text-2xl font-bold text-white">{stats.top_users?.length || 0}</p>
          </div>
          <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-400 text-sm">Resource Types</p>
            <p className="text-2xl font-bold text-white">
              {Object.keys(stats.by_resource_type || {}).length}
            </p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-slate-900 rounded-lg p-4 mb-6 border border-slate-700">
        <div className="flex gap-3 flex-wrap">
          <select
            value={actionFilter}
            onChange={(e) => {
              setActionFilter(e.target.value)
              setPage(0)
            }}
            className="bg-slate-800 text-white border border-slate-600 rounded px-3 py-2 text-sm"
          >
            <option value="">All Actions</option>
            <option value="CREATE">Create</option>
            <option value="UPDATE">Update</option>
            <option value="DELETE">Delete</option>
          </select>
          <select
            value={resourceFilter}
            onChange={(e) => {
              setResourceFilter(e.target.value)
              setPage(0)
            }}
            className="bg-slate-800 text-white border border-slate-600 rounded px-3 py-2 text-sm"
          >
            <option value="">All Resources</option>
            <option value="Incident">Incident</option>
            <option value="Vulnerability">Vulnerability</option>
            <option value="User">User</option>
          </select>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-slate-900 rounded-lg border border-slate-700 overflow-hidden">
        {loading ? (
          <div className="text-center py-12">
            <p className="text-slate-400">Loading audit logs...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-400">No audit logs found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700 bg-slate-800">
                  <th className="px-6 py-3 text-left text-slate-300 font-medium">Timestamp</th>
                  <th className="px-6 py-3 text-left text-slate-300 font-medium">Action</th>
                  <th className="px-6 py-3 text-left text-slate-300 font-medium">Resource</th>
                  <th className="px-6 py-3 text-left text-slate-300 font-medium">User</th>
                  <th className="px-6 py-3 text-left text-slate-300 font-medium">Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} className="border-b border-slate-700 hover:bg-slate-800/50">
                    <td className="px-6 py-4 text-slate-300">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getActionColor(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-300">
                      {log.resource_type}
                    </td>
                    <td className="px-6 py-4 text-slate-400 text-xs">
                      {log.user_id.substring(0, 8)}...
                    </td>
                    <td className="px-6 py-4">
                      {log.new_values && (
                        <button className="text-red-400 hover:text-red-300 text-xs">
                          View Changes
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination */}
      {!loading && logs.length > 0 && (
        <div className="flex items-center justify-between mt-6 bg-slate-900 rounded-lg p-4 border border-slate-700">
          <div className="text-sm text-slate-400">
            Showing {page * pageSize + 1}-{Math.min((page + 1) * pageSize, total)} of {total}
          </div>
          <div className="flex gap-2">
            <Button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              variant="outline"
              className="border-slate-600 text-slate-300"
            >
              ← Previous
            </Button>
            <Button
              onClick={() => setPage(page + 1)}
              disabled={logs.length < pageSize}
              variant="outline"
              className="border-slate-600 text-slate-300"
            >
              Next →
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
