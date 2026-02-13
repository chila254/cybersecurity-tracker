interface StatsCardProps {
  title: string
  value: number | string
  icon: string
  trend?: {
    value: number
    label: string
    positive: boolean
  }
  bgColor?: string
}

export function StatsCard({
  title,
  value,
  icon,
  trend,
  bgColor = 'bg-red-900/20',
}: StatsCardProps) {
  return (
    <div className={`${bgColor} rounded-lg p-6 border border-red-900/30`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-slate-400 text-sm mb-2">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {trend && (
            <p className={`text-xs mt-2 ${trend.positive ? 'text-green-400' : 'text-red-400'}`}>
              {trend.positive ? '↑' : '↓'} {trend.value} {trend.label}
            </p>
          )}
        </div>
        <div className="text-3xl opacity-20">{icon}</div>
      </div>
    </div>
  )
}
