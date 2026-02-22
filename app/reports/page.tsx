'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Download, RefreshCw } from 'lucide-react'

interface ReportData {
  [key: string]: any
}

export default function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState<string>('monthly-summary')
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [loading, setLoading] = useState(false)

  const reports = [
    {
      id: 'monthly-summary',
      title: 'Monthly Security Summary',
      description: 'Overview of incidents, vulnerabilities, and team activities',
      icon: '📊',
    },
    {
      id: 'incident-analysis',
      title: 'Incident Analysis Report',
      description: 'Detailed analysis of incidents by severity, type, and resolution time',
      icon: '🚨',
    },
    {
      id: 'vulnerability-status',
      title: 'Vulnerability Status Report',
      description: 'Current state of vulnerabilities including patch coverage and CVE details',
      icon: '⚠️',
    },
    {
      id: 'compliance-audit',
      title: 'Compliance & Audit Log',
      description: 'Complete audit trail for compliance requirements and investigations',
      icon: '📋',
    },
    {
      id: 'team-performance',
      title: 'Team Performance Metrics',
      description: 'Team productivity, response times, and resolution metrics',
      icon: '👥',
    },
  ]

  useEffect(() => {
    fetchReport(selectedReport)
  }, [selectedReport])

  const fetchReport = async (reportId: string) => {
    setLoading(true)
    try {
      let endpoint = `/reports/${reportId}`
      const { data } = await apiClient.get(endpoint)
      setReportData(data)
    } catch (error) {
      console.error('Failed to fetch report:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExportCSV = async (reportId: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/reports/${reportId}/export/csv`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${reportId}-${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Failed to export report:', error)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Reports & Analytics</h1>
        <p className="text-slate-400">Generate compliance reports and security analytics</p>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {reports.map((report) => (
          <div
            key={report.id}
            onClick={() => setSelectedReport(report.id)}
            className={`bg-slate-900 rounded-lg p-6 border transition-colors cursor-pointer ${
              selectedReport === report.id
                ? 'border-red-600'
                : 'border-slate-700 hover:border-slate-600'
            }`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="text-4xl">{report.icon}</div>
              {selectedReport === report.id && (
                <span className="px-2 py-1 bg-red-600/20 text-red-300 text-xs rounded">
                  Active
                </span>
              )}
            </div>
            <h3 className="text-lg font-bold text-white mb-2">{report.title}</h3>
            <p className="text-slate-400 text-sm">{report.description}</p>
          </div>
        ))}
      </div>

      {/* Report Data Display */}
      {reportData && (
        <div className="bg-slate-900 rounded-lg p-6 border border-slate-700 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">
              {reports.find(r => r.id === selectedReport)?.title}
            </h2>
            <div className="flex gap-2">
              <Button
                onClick={() => fetchReport(selectedReport)}
                className="bg-slate-700 hover:bg-slate-600 text-white"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button
                onClick={() => handleExportCSV(selectedReport)}
                className="bg-red-600 hover:bg-red-700 text-white"
              >
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <p className="text-slate-400">Loading report data...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <pre className="bg-slate-800 p-4 rounded text-sm text-slate-300 overflow-auto max-h-96">
                {JSON.stringify(reportData, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
