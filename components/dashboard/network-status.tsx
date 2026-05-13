'use client'

import { Wifi, WifiOff, Shield, AlertTriangle } from 'lucide-react'

export function NetworkStatus() {
  // Mock data - in real app this would come from API
  const networkStatus = {
    connected: true,
    devices: 24,
    alerts: 2,
    lastScan: new Date().toLocaleTimeString()
  }

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-white">Network Status</h2>
        {networkStatus.connected ? (
          <Wifi className="w-5 h-5 text-green-400" />
        ) : (
          <WifiOff className="w-5 h-5 text-red-400" />
        )}
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-slate-400 text-sm">Status</span>
          <span className="text-green-400 text-sm font-medium">Online</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-slate-400 text-sm">Connected Devices</span>
          <span className="text-white text-sm font-medium">{networkStatus.devices}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-slate-400 text-sm">Active Alerts</span>
          <div className="flex items-center gap-1">
            {networkStatus.alerts > 0 && (
              <AlertTriangle className="w-4 h-4 text-orange-400" />
            )}
            <span className={`text-sm font-medium ${networkStatus.alerts > 0 ? 'text-orange-400' : 'text-green-400'}`}>
              {networkStatus.alerts}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-slate-400 text-sm">Last Scan</span>
          <span className="text-white text-sm font-medium">{networkStatus.lastScan}</span>
        </div>

        <div className="pt-4 border-t border-slate-700">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-green-400" />
            <span className="text-green-400 text-sm font-medium">Network Secure</span>
          </div>
        </div>
      </div>
    </div>
  )
}