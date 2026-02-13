'use client'

import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Link from 'next/link'

export default function Home() {
  const { isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-red-600">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <span className="text-xl font-bold text-white">IncidentTracker</span>
          </div>
          <div className="flex gap-4">
            <Link
              href="/login"
              className="px-4 py-2 rounded border border-slate-600 text-slate-300 hover:text-white hover:border-slate-500 transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 rounded bg-red-600 hover:bg-red-700 text-white font-medium transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="max-w-2xl">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Enterprise Security Incident Management
          </h1>
          <p className="text-xl text-slate-400 mb-8 leading-relaxed">
            Streamline your cybersecurity operations with real-time incident tracking, vulnerability management, 
            and comprehensive team collaboration. Built for modern security teams.
          </p>
          <div className="flex gap-4">
            <Link
              href="/register"
              className="px-6 py-3 rounded-lg bg-red-600 hover:bg-red-700 text-white font-medium transition-colors"
            >
              Start Free
            </Link>
            <a
              href="#features"
              className="px-6 py-3 rounded-lg border border-slate-600 text-white hover:border-slate-500 transition-colors font-medium"
            >
              Learn More
            </a>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="bg-slate-900/50 py-20 border-y border-slate-700">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-white mb-12 text-center">Powerful Features</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon="📊"
              title="Real-time Dashboard"
              description="Monitor incidents and vulnerabilities with live statistics and trends"
            />
            <FeatureCard
              icon="🚨"
              title="Incident Management"
              description="Create, track, and resolve security incidents with team collaboration"
            />
            <FeatureCard
              icon="⚠️"
              title="Vulnerability Tracking"
              description="Manage CVEs, track patches, and monitor remediation progress"
            />
            <FeatureCard
              icon="👥"
              title="Team Collaboration"
              description="Comments, assignments, and detailed incident timelines for your team"
            />
            <FeatureCard
              icon="📋"
              title="Compliance Reports"
              description="Generate audit logs and detailed reports for compliance requirements"
            />
            <FeatureCard
              icon="🔗"
              title="Integrations"
              description="Connect with your existing security tools via webhooks and APIs"
            />
          </div>
        </div>
      </div>

      {/* Security Section */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="bg-slate-800 rounded-lg p-12 border border-slate-700">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-white mb-4">Built with Security in Mind</h2>
            <p className="text-slate-400 mb-8">
              Enterprise-grade security with role-based access control, encryption, audit logging, 
              and multi-tenant isolation. Your data is protected.
            </p>
            <div className="grid md:grid-cols-3 gap-6 mt-8">
              <SecurityFeature icon="🔐" title="End-to-End Encryption" />
              <SecurityFeature icon="👤" title="Role-Based Access" />
              <SecurityFeature icon="📝" title="Audit Logging" />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-slate-900 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-slate-400 text-sm">
          <p>&copy; 2024 IncidentTracker. Enterprise Security Platform. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
      <p className="text-slate-400 text-sm">{description}</p>
    </div>
  )
}

function SecurityFeature({ icon, title }: { icon: string; title: string }) {
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="text-3xl">{icon}</div>
      <p className="text-sm font-medium text-white">{title}</p>
    </div>
  )
}
