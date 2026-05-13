'use client'

import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  color: 'red' | 'orange' | 'yellow' | 'green' | 'blue' | 'purple'
  trend?: string
  description?: string
}

export function StatsCard({ title, value, icon: Icon, color, trend, description }: StatsCardProps) {
  const colorClasses = {
    red: {
      bg: 'bg-red-500/10',
      border: 'border-red-500/20',
      icon: 'text-red-400',
      trend: trend?.startsWith('+') ? 'text-red-400' : 'text-green-400'
    },
    orange: {
      bg: 'bg-orange-500/10',
      border: 'border-orange-500/20',
      icon: 'text-orange-400',
      trend: trend?.startsWith('+') ? 'text-orange-400' : 'text-green-400'
    },
    yellow: {
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/20',
      icon: 'text-yellow-400',
      trend: trend?.startsWith('+') ? 'text-yellow-400' : 'text-green-400'
    },
    green: {
      bg: 'bg-green-500/10',
      border: 'border-green-500/20',
      icon: 'text-green-400',
      trend: trend?.startsWith('+') ? 'text-green-400' : 'text-red-400'
    },
    blue: {
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/20',
      icon: 'text-blue-400',
      trend: trend?.startsWith('+') ? 'text-blue-400' : 'text-green-400'
    },
    purple: {
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20',
      icon: 'text-purple-400',
      trend: trend?.startsWith('+') ? 'text-purple-400' : 'text-green-400'
    }
  }

  const classes = colorClasses[color]

  return (
    <div className={`${classes.bg} border ${classes.border} rounded-xl p-6 hover:shadow-lg transition-all duration-200`}>
      <div className="flex items-center justify-between mb-4">
        <div className={`p-2 rounded-lg ${classes.bg} border ${classes.border}`}>
          <Icon className={`w-6 h-6 ${classes.icon}`} />
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-sm font-medium ${classes.trend}`}>
            {trend.startsWith('+') ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            {trend}
          </div>
        )}
      </div>

      <div className="space-y-1">
        <p className="text-2xl font-bold text-white">{value}</p>
        <p className="text-sm font-medium text-slate-300">{title}</p>
        {description && (
          <p className="text-xs text-slate-400">{description}</p>
        )}
      </div>
    </div>
  )
}