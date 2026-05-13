'use client'

// Charts temporarily disabled due to build issues
// import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

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
  const severityData = data?.severity_distribution || []

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-white">Security Overview</h2>
          <p className="text-slate-400 text-sm">Incident trends and severity distribution</p>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {severityData.map((item) => (
          <div key={item.severity} className="text-center p-4 bg-slate-800 rounded-lg">
            <div
              className="w-3 h-3 rounded-full mx-auto mb-2"
              style={{ backgroundColor: '#ef4444' }}
            ></div>
            <p className="text-sm font-medium text-slate-300">{item.severity}</p>
            <p className="text-lg font-bold text-white">{item.count}</p>
          </div>
        ))}
        {severityData.length === 0 && (
          <>
            <div className="text-center p-4 bg-slate-800 rounded-lg">
              <div className="w-3 h-3 rounded-full mx-auto mb-2 bg-red-500"></div>
              <p className="text-sm font-medium text-slate-300">Critical</p>
              <p className="text-lg font-bold text-white">0</p>
            </div>
            <div className="text-center p-4 bg-slate-800 rounded-lg">
              <div className="w-3 h-3 rounded-full mx-auto mb-2 bg-orange-500"></div>
              <p className="text-sm font-medium text-slate-300">High</p>
              <p className="text-lg font-bold text-white">0</p>
            </div>
            <div className="text-center p-4 bg-slate-800 rounded-lg">
              <div className="w-3 h-3 rounded-full mx-auto mb-2 bg-yellow-500"></div>
              <p className="text-sm font-medium text-slate-300">Medium</p>
              <p className="text-lg font-bold text-white">0</p>
            </div>
            <div className="text-center p-4 bg-slate-800 rounded-lg">
              <div className="w-3 h-3 rounded-full mx-auto mb-2 bg-blue-500"></div>
              <p className="text-sm font-medium text-slate-300">Low</p>
              <p className="text-lg font-bold text-white">0</p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}