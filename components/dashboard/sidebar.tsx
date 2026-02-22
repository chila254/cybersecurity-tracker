'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'
import { Button } from '@/components/ui/button'

export function Sidebar() {
  const router = useRouter()
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-700 h-screen fixed left-0 top-0 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-red-600">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div>
            <h1 className="text-white font-bold text-sm">IncidentTracker</h1>
            <p className="text-xs text-slate-400">Security Dashboard</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-6 space-y-2">
        <NavItem href="/dashboard" icon="📊" label="Dashboard" />
        <NavItem href="/incidents" icon="🚨" label="Incidents" />
        <NavItem href="/vulnerabilities" icon="⚠️" label="Vulnerabilities" />
        <NavItem href="/network" icon="🌐" label="Network Monitor" />
        <NavItem href="/reports" icon="📋" label="Reports" />
        <NavItem href="/settings" icon="⚙️" label="Settings" />
      </nav>

      {/* User Info & Logout */}
      <div className="p-6 border-t border-slate-700">
        <div className="mb-4 pb-4 border-b border-slate-700">
          <p className="text-xs text-slate-400">Logged in as</p>
          <p className="text-sm font-medium text-white truncate">{user?.email}</p>
          <p className="text-xs text-slate-400">
            {user?.role === 'ADMIN' && '🔴 Administrator'}
            {user?.role === 'ANALYST' && '🟡 Security Analyst'}
            {user?.role === 'VIEWER' && '🔵 Viewer'}
          </p>
        </div>
        <Button
          onClick={handleLogout}
          variant="outline"
          className="w-full border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white"
        >
          Logout
        </Button>
      </div>
    </aside>
  )
}

function NavItem({
  href,
  icon,
  label,
}: {
  href: string
  icon: string
  label: string
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 px-4 py-2 rounded-lg text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
    >
      <span>{icon}</span>
      <span className="text-sm font-medium">{label}</span>
    </Link>
  )
}
