'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface SecurityOverviewProps {
  data: {
    incident_trends?: Array<{ date: string; count: number }>
    severity_distribution?: Array<{ severity: string; count: number }>
  } | null
}

const severityColors = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#eab308',
  LOW: '#3b82f6',
  INFO: '#64748b'
}

export function SecurityOverview({ data }: SecurityOverviewProps) {
  const incidentTrends = data?.incident_trends || []
  const severityData = data?.severity_distribution || []

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-white">Security Overview</h2>
          <p className="text-slate-400 text-sm">Incident trends and severity distribution</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Incident Trends Chart */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-300">Incident Trends</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={incidentTrends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="date"
                  stroke="#9ca3af"
                  fontSize={12}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f1f5f9'
                  }}
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Bar
                  dataKey="count"
                  fill="#ef4444"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-300">Severity Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="count"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={severityColors[entry.severity as keyof typeof severityColors] || '#64748b'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f1f5f9'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-2 lg:grid-cols-4 gap-4 pt-6 border-t border-slate-700">
        {severityData.map((item) => (
          <div key={item.severity} className="text-center">
            <div
              className="w-3 h-3 rounded-full mx-auto mb-2"
              style={{ backgroundColor: severityColors[item.severity as keyof typeof severityColors] || '#64748b' }}
            ></div>
            <p className="text-sm font-medium text-slate-300">{item.severity}</p>
            <p className="text-lg font-bold text-white">{item.count}</p>
          </div>
        ))}
      </div>
    </div>
  )
}