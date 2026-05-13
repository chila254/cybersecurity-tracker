'use client'

import { useAuth } from '@/lib/auth-context'

export const dynamic = 'force-dynamic'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Link from 'next/link'
import { Shield, Lock, Users, FileText, BarChart3, AlertCircle, AlertTriangle, FileText as FileTextIcon } from 'lucide-react'

export default function Home() {
  const { isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Navigation */}
      <nav className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-red-700 rounded-xl flex items-center justify-center shadow-lg">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">CyberSec</span>
          </div>
          <div className="flex gap-4">
            <Link
              href="/login"
              className="px-4 py-2 rounded-lg border border-slate-600 text-slate-300 hover:text-white hover:border-slate-500 transition-all duration-200 font-medium"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-medium transition-all duration-200 shadow-lg"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 mb-6">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-red-400 text-sm font-medium">Enterprise Security Platform</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Cybersecurity
            <span className="bg-gradient-to-r from-red-400 to-red-600 bg-clip-text text-transparent"> Incident</span>
            <br />Management
          </h1>
          <p className="text-xl text-slate-400 mb-8 leading-relaxed max-w-2xl">
            Streamline your cybersecurity operations with real-time incident tracking, vulnerability management,
            and comprehensive team collaboration. Built for modern security teams.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href="/register"
              className="px-8 py-4 rounded-xl bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white font-semibold transition-all duration-200 shadow-lg hover:shadow-red-500/25 transform hover:-translate-y-0.5"
            >
              Start Free Trial
            </Link>
            <a
              href="#features"
              className="px-8 py-4 rounded-xl border border-slate-600 text-white hover:border-slate-500 transition-all duration-200 font-semibold hover:bg-slate-800"
            >
              Watch Demo
            </a>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="bg-slate-900/30 py-24 border-y border-slate-700/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Powerful Security Features
            </h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Everything you need to manage cybersecurity incidents, vulnerabilities, and team collaboration in one platform.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon="bar-chart-2"
              title="Real-time Dashboard"
              description="Monitor incidents and vulnerabilities with live statistics, trends, and predictive analytics"
            />
            <FeatureCard
              icon="alert-circle"
              title="Incident Management"
              description="Create, track, and resolve security incidents with automated workflows and team collaboration"
            />
            <FeatureCard
              icon="alert-triangle"
              title="Vulnerability Tracking"
              description="Manage CVEs, track patches, and monitor remediation progress with automated scanning"
            />
            <FeatureCard
              icon="users"
              title="Team Collaboration"
              description="Comments, assignments, detailed incident timelines, and role-based access control"
            />
            <FeatureCard
              icon="clipboard"
              title="Compliance Reports"
              description="Generate audit logs, compliance reports, and detailed analytics for regulatory requirements"
            />
            <FeatureCard
              icon="link"
              title="Integrations"
              description="Connect with SIEM, SOAR, ticketing systems, and other security tools via APIs and webhooks"
            />
          </div>
        </div>
      </div>

      {/* Security Section */}
      <div className="max-w-7xl mx-auto px-6 py-24">
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-12 border border-slate-700 shadow-2xl">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 border border-green-500/20 mb-6">
              <Shield className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-sm font-medium">Enterprise Security</span>
            </div>
            <h2 className="text-4xl font-bold text-white mb-6">Built with Security in Mind</h2>
            <p className="text-xl text-slate-400 mb-12 leading-relaxed">
              Enterprise-grade security with role-based access control, end-to-end encryption, audit logging,
              and multi-tenant isolation. Your sensitive security data is always protected.
            </p>
            <div className="grid md:grid-cols-3 gap-8 mt-12">
              <SecurityFeature icon="lock" title="End-to-End Encryption" description="AES-256 encryption for all data" />
              <SecurityFeature icon="user" title="Role-Based Access" description="Granular permissions and controls" />
              <SecurityFeature icon="file-text" title="Audit Logging" description="Complete activity tracking" />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700/50 bg-slate-900/50 backdrop-blur py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-red-600 to-red-700 rounded-lg flex items-center justify-center">
                <Shield className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-bold text-white">CyberSec</span>
            </div>
            <div className="flex items-center gap-8 text-sm text-slate-400">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Security</a>
              <a href="#" className="hover:text-white transition-colors">Support</a>
            </div>
          </div>
          <div className="border-t border-slate-700/50 mt-8 pt-8 text-center text-slate-500 text-sm">
            <p>&copy; 2026 CyberSec. Enterprise Security Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  const getIcon = (iconName: string) => {
    const iconStyles = 'w-8 h-8 text-red-400'
    switch (iconName) {
      case 'bar-chart-2':
        return <BarChart3 className={iconStyles} />
      case 'alert-circle':
        return <AlertCircle className={iconStyles} />
      case 'alert-triangle':
        return <AlertTriangle className={iconStyles} />
      case 'users':
        return <Users className={iconStyles} />
      case 'clipboard':
        return <FileText className={iconStyles} />
      case 'link':
        return <Link className={iconStyles} />
      default:
        return null
    }
  }

  return (
    <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 hover:border-slate-600 hover:bg-slate-800/70 transition-all duration-300 hover:shadow-lg hover:shadow-red-500/5">
      <div className="mb-4 p-3 bg-red-500/10 rounded-lg w-fit">
        {getIcon(icon)}
      </div>
      <h3 className="text-xl font-bold text-white mb-3">{title}</h3>
      <p className="text-slate-400 leading-relaxed">{description}</p>
    </div>
  )
}

function SecurityFeature({ icon, title, description }: { icon: string; title: string; description?: string }) {
  const getIcon = (iconName: string) => {
    const iconStyles = 'w-8 h-8 text-green-400'
    switch (iconName) {
      case 'lock':
        return <Lock className={iconStyles} />
      case 'user':
        return <Users className={iconStyles} />
      case 'file-text':
        return <FileTextIcon className={iconStyles} />
      default:
        return null
    }
  }

  return (
    <div className="text-center p-6 rounded-xl bg-slate-800/30 border border-slate-700/50 hover:border-green-500/30 transition-all duration-300">
      <div className="mb-4 flex justify-center">
        {getIcon(icon)}
      </div>
      <h4 className="text-lg font-semibold text-white mb-2">{title}</h4>
      {description && (
        <p className="text-slate-400 text-sm">{description}</p>
      )}
    </div>
  )
}
