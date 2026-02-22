'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'

interface Incident {
  id: string
  title: string
  description: string
  severity: string
  status: string
  incident_type: string
  created_at: string
  updated_at: string
  assigned_to?: string
  affected_systems: string[]
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    severity: 'MEDIUM',
    incident_type: 'other',
  })
  
  // Search and filter
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [filterSeverity, setFilterSeverity] = useState('')
  const [filterType, setFilterType] = useState('')
  
  // Pagination
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(10)
  const [totalIncidents, setTotalIncidents] = useState(0)

  useEffect(() => {
    fetchIncidents()
  }, [search, filterStatus, filterSeverity, filterType, page])

  const fetchIncidents = async () => {
    setLoading(true)
    try {
      let url = '/incidents'
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (filterStatus) params.append('status', filterStatus)
      if (filterSeverity) params.append('severity', filterSeverity)
      if (filterType) params.append('incident_type', filterType)
      params.append('skip', (page * pageSize).toString())
      params.append('limit', pageSize.toString())
      
      if (params.toString()) url += '?' + params.toString()

      const { data } = await apiClient.get<Incident[]>(url)
      if (data) {
        setIncidents(data)
        setTotalIncidents(data.length)
      }
    } catch (error) {
      console.error('Failed to fetch incidents:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
    setPage(0) // Reset to first page on new search
  }

  const handleCreateIncident = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiClient.post('/incidents', formData)
      setShowModal(false)
      setFormData({ title: '', description: '', severity: 'MEDIUM', incident_type: 'other' })
      fetchIncidents()
    } catch (error) {
      console.error('Failed to create incident:', error)
    }
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
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Incidents</h1>
          <p className="text-slate-400">Manage security incidents and investigations</p>
        </div>
        <Button
          onClick={() => setShowModal(true)}
          className="bg-red-600 hover:bg-red-700 text-white"
        >
          + New Incident
        </Button>
      </div>

      {/* Search & Filters */}
      <div className="bg-slate-900 rounded-lg p-4 mb-6 border border-slate-700">
        <div className="flex gap-3 mb-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <Input
              type="text"
              placeholder="Search by title or description..."
              value={search}
              onChange={handleSearch}
              className="bg-slate-800 border-slate-600 text-white pl-10"
            />
          </div>
        </div>
        <div className="flex gap-3 flex-wrap">
          <select
            value={filterStatus}
            onChange={(e) => {
              setFilterStatus(e.target.value)
              setPage(0)
            }}
            className="bg-slate-800 text-white border border-slate-600 rounded px-3 py-2 text-sm"
          >
            <option value="">All Status</option>
            <option value="OPEN">Open</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
          </select>
          <select
            value={filterSeverity}
            onChange={(e) => {
              setFilterSeverity(e.target.value)
              setPage(0)
            }}
            className="bg-slate-800 text-white border border-slate-600 rounded px-3 py-2 text-sm"
          >
            <option value="">All Severity</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
          <select
            value={filterType}
            onChange={(e) => {
              setFilterType(e.target.value)
              setPage(0)
            }}
            className="bg-slate-800 text-white border border-slate-600 rounded px-3 py-2 text-sm"
          >
            <option value="">All Types</option>
            <option value="data_breach">Data Breach</option>
            <option value="malware">Malware</option>
            <option value="unauthorized_access">Unauthorized Access</option>
            <option value="denial_of_service">Denial of Service</option>
            <option value="social_engineering">Social Engineering</option>
            <option value="configuration_error">Configuration Error</option>
            <option value="supply_chain">Supply Chain</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      {/* Incidents List */}
      <div className="space-y-3">
        {loading ? (
          <div className="text-center py-12">
            <p className="text-slate-400">Loading incidents...</p>
          </div>
        ) : incidents.length === 0 ? (
          <div className="text-center py-12 bg-slate-900 rounded-lg border border-slate-700">
            <p className="text-slate-400">No incidents found</p>
          </div>
        ) : (
          incidents.map((incident) => (
            <div
              key={incident.id}
              className="bg-slate-900 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white mb-2">{incident.title}</h3>
                  <p className="text-slate-400 text-sm mb-4">{incident.description}</p>
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span>📅 {new Date(incident.created_at).toLocaleDateString()}</span>
                    <span>•</span>
                    <span>🏷️ {incident.incident_type}</span>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getSeverityColor(incident.severity)}`}>
                    {incident.severity}
                  </span>
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(incident.status)}`}>
                    {incident.status}
                  </span>
                </div>
              </div>
              {incident.affected_systems && incident.affected_systems.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <p className="text-xs text-slate-400 mb-2">Affected Systems:</p>
                  <div className="flex gap-2 flex-wrap">
                    {incident.affected_systems.map((system) => (
                      <span key={system} className="px-2 py-1 bg-slate-800 rounded text-xs text-slate-300">
                        {system}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {!loading && incidents.length > 0 && (
        <div className="flex items-center justify-between mt-6 bg-slate-900 rounded-lg p-4 border border-slate-700">
          <div className="text-sm text-slate-400">
            Showing {page * pageSize + 1}-{Math.min((page + 1) * pageSize, totalIncidents)} of {totalIncidents}
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
              disabled={incidents.length < pageSize}
              variant="outline"
              className="border-slate-600 text-slate-300"
            >
              Next →
            </Button>
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-900 rounded-lg p-6 max-w-md w-full mx-4 border border-slate-700">
            <h2 className="text-xl font-bold text-white mb-4">Create New Incident</h2>
            <form onSubmit={handleCreateIncident} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Title</label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Incident title"
                  required
                  className="bg-slate-800 border-slate-600 text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Detailed description"
                  required
                  className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white text-sm"
                  rows={4}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Severity</label>
                <select
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white text-sm"
                >
                  <option value="CRITICAL">Critical</option>
                  <option value="HIGH">High</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="LOW">Low</option>
                </select>
              </div>
              <div className="flex gap-3">
                <Button
                  type="button"
                  onClick={() => setShowModal(false)}
                  variant="outline"
                  className="flex-1 border-slate-600 text-slate-300"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                >
                  Create
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
