'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'

export default function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState<string | null>(null)

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
      id: 'vuln-status',
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
    {
      id: 'trending-threats',
      title: 'Trending Threats Analysis',
      description: 'Analysis of trending incidents and vulnerabilities affecting your organization',
      icon: '📈',
    },
  ]

  const handleGenerateReport = (reportId: string) => {
    setSelectedReport(reportId)
    // In production, this would trigger report generation and download
    setTimeout(() => {
      alert(`Report "${reportId}" would be generated and downloaded as PDF`)
      setSelectedReport(null)
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Reports & Analytics</h1>
        <p className="text-slate-400">Generate compliance reports and security analytics</p>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reports.map((report) => (
          <div
            key={report.id}
            className="bg-slate-900 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="text-4xl">{report.icon}</div>
              <Button
                onClick={() => handleGenerateReport(report.id)}
                disabled={selectedReport === report.id}
                className="bg-red-600 hover:bg-red-700 text-white text-sm"
              >
                {selectedReport === report.id ? 'Generating...' : 'Generate'}
              </Button>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">{report.title}</h3>
            <p className="text-slate-400 text-sm">{report.description}</p>
          </div>
        ))}
      </div>

      {/* Export Options */}
      <div className="mt-12 bg-slate-900 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-bold text-white mb-4">Export Options</h2>
        <p className="text-slate-400 mb-6">Export raw data for external analysis and auditing</p>
        <div className="flex gap-4 flex-wrap">
          <Button className="bg-slate-700 hover:bg-slate-600 text-white">
            Export as CSV
          </Button>
          <Button className="bg-slate-700 hover:bg-slate-600 text-white">
            Export as JSON
          </Button>
          <Button className="bg-slate-700 hover:bg-slate-600 text-white">
            Export Audit Log
          </Button>
        </div>
      </div>
    </div>
  )
}
