'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'

interface Vulnerability {
  id: string
  cve_id?: string
  title: string
  description?: string
  cvss_score?: number
  severity: string
  status: string
  affected_systems: string[]
  remediation?: string
  discovered_date: string
  patched_date?: string
}

export default function VulnerabilitiesPage() {
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    cve_id: '',
    title: '',
    description: '',
    cvss_score: '',
    severity: 'MEDIUM',
    status: 'UNPATCHED',
  })
  
  // Search and filter
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [filterSeverity, setFilterSeverity] = useState('')
  
  // Pagination
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(10)
  const [totalVulns, setTotalVulns] = useState(0)

  useEffect(() => {
    fetchVulnerabilities()
  }, [search, filterStatus, filterSeverity, page])

  const fetchVulnerabilities = async () => {
    setLoading(true)
    try {
      let url = '/vulnerabilities'
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (filterStatus) params.append('status', filterStatus)
      if (filterSeverity) params.append('severity', filterSeverity)
      params.append('skip', (page * pageSize).toString())
      params.append('limit', pageSize.toString())
      
      if (params.toString()) url += '?' + params.toString()

      const { data } = await apiClient.get<Vulnerability[]>(url)
      if (data) {
        setVulnerabilities(data)
        setTotalVulns(data.length)
      }
    } catch (error) {
      console.error('Failed to fetch vulnerabilities:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
    setPage(0) // Reset to first page on new search
  }

  const handleCreateVulnerability = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiClient.post('/vulnerabilities', {
        cve_id: formData.cve_id || null,
        title: formData.title,
        description: formData.description,
        cvss_score: formData.cvss_score ? parseFloat(formData.cvss_score) : null,
        severity: formData.severity,
        status: formData.status,
      })
      setShowModal(false)
      setFormData({
        cve_id: '',
        title: '',
        description: '',
        cvss_score: '',
        severity: 'MEDIUM',
        status: 'UNPATCHED',
      })
      fetchVulnerabilities()
    } catch (error) {
      console.error('Failed to create vulnerability:', error)
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
      case 'INFO':
        return 'text-slate-400 bg-slate-900/20'
      default:
        return 'text-slate-400 bg-slate-900/20'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'UNPATCHED':
        return 'bg-red-900/20 text-red-300'
      case 'PATCHED':
        return 'bg-green-900/20 text-green-300'
      case 'MITIGATED':
        return 'bg-blue-900/20 text-blue-300'
      case 'MONITORING':
        return 'bg-yellow-900/20 text-yellow-300'
      default:
        return 'bg-slate-700/20 text-slate-300'
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Vulnerabilities</h1>
          <p className="text-slate-400">Track CVEs and vulnerability management</p>
        </div>
        <Button
          onClick={() => setShowModal(true)}
          className="bg-red-600 hover:bg-red-700 text-white"
        >
          + New Vulnerability
        </Button>
      </div>

      {/* Search & Filters */}
      <div className="bg-slate-900 rounded-lg p-4 mb-6 border border-slate-700">
        <div className="flex gap-3 mb-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <Input
              type="text"
              placeholder="Search by CVE ID, title, or description..."
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
            <option value="UNPATCHED">Unpatched</option>
            <option value="PATCHED">Patched</option>
            <option value="MITIGATED">Mitigated</option>
            <option value="MONITORING">Monitoring</option>
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
            <option value="INFO">Info</option>
          </select>
        </div>
      </div>

      {/* Vulnerabilities List */}
      <div className="space-y-3">
        {loading ? (
          <div className="text-center py-12">
            <p className="text-slate-400">Loading vulnerabilities...</p>
          </div>
        ) : vulnerabilities.length === 0 ? (
          <div className="text-center py-12 bg-slate-900 rounded-lg border border-slate-700">
            <p className="text-slate-400">No vulnerabilities found</p>
          </div>
        ) : (
          vulnerabilities.map((vuln) => (
            <div
              key={vuln.id}
              className="bg-slate-900 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-bold text-white">{vuln.title}</h3>
                    {vuln.cve_id && (
                      <span className="px-2 py-1 bg-slate-800 rounded text-xs text-slate-300 font-mono">
                        {vuln.cve_id}
                      </span>
                    )}
                  </div>
                  {vuln.description && (
                    <p className="text-slate-400 text-sm mb-4">{vuln.description}</p>
                  )}
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span>📅 {new Date(vuln.discovered_date).toLocaleDateString()}</span>
                    {vuln.cvss_score && (
                      <>
                        <span>•</span>
                        <span>📊 CVSS {vuln.cvss_score}</span>
                      </>
                    )}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getSeverityColor(vuln.severity)}`}>
                    {vuln.severity}
                  </span>
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(vuln.status)}`}>
                    {vuln.status}
                  </span>
                </div>
              </div>
              {vuln.affected_systems && vuln.affected_systems.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <p className="text-xs text-slate-400 mb-2">Affected Systems:</p>
                  <div className="flex gap-2 flex-wrap">
                    {vuln.affected_systems.map((system) => (
                      <span key={system} className="px-2 py-1 bg-slate-800 rounded text-xs text-slate-300">
                        {system}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {vuln.remediation && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <p className="text-xs text-slate-400 mb-2">Remediation:</p>
                  <p className="text-sm text-slate-300">{vuln.remediation}</p>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {!loading && vulnerabilities.length > 0 && (
        <div className="flex items-center justify-between mt-6 bg-slate-900 rounded-lg p-4 border border-slate-700">
          <div className="text-sm text-slate-400">
            Showing {page * pageSize + 1}-{Math.min((page + 1) * pageSize, totalVulns)} of {totalVulns}
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
              disabled={vulnerabilities.length < pageSize}
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
            <h2 className="text-xl font-bold text-white mb-4">Create New Vulnerability</h2>
            <form onSubmit={handleCreateVulnerability} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">CVE ID (optional)</label>
                <Input
                  value={formData.cve_id}
                  onChange={(e) => setFormData({ ...formData, cve_id: e.target.value })}
                  placeholder="CVE-XXXX-XXXXX"
                  className="bg-slate-800 border-slate-600 text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Title</label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Vulnerability title"
                  required
                  className="bg-slate-800 border-slate-600 text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Details"
                  className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white text-sm"
                  rows={3}
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
                  <option value="INFO">Info</option>
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
