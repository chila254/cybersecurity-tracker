'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/auth-context'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function SettingsPage() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('profile')
  const [notifications, setNotifications] = useState({
    emailOnNewIncident: true,
    emailOnCriticalVuln: true,
    emailOnIncidentUpdate: true,
    emailDigest: true,
  })

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-slate-400">Manage your account and preferences</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-8 border-b border-slate-700">
        <button
          onClick={() => setActiveTab('profile')}
          className={`px-4 py-2 border-b-2 font-medium transition-colors ${
            activeTab === 'profile'
              ? 'border-red-600 text-white'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Profile
        </button>
        <button
          onClick={() => setActiveTab('notifications')}
          className={`px-4 py-2 border-b-2 font-medium transition-colors ${
            activeTab === 'notifications'
              ? 'border-red-600 text-white'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Notifications
        </button>
        <button
          onClick={() => setActiveTab('security')}
          className={`px-4 py-2 border-b-2 font-medium transition-colors ${
            activeTab === 'security'
              ? 'border-red-600 text-white'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Security
        </button>
        <button
          onClick={() => setActiveTab('integrations')}
          className={`px-4 py-2 border-b-2 font-medium transition-colors ${
            activeTab === 'integrations'
              ? 'border-red-600 text-white'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Integrations
        </button>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="max-w-2xl">
          <div className="bg-slate-900 rounded-lg p-6 border border-slate-700">
            <h2 className="text-xl font-bold text-white mb-6">Profile Information</h2>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
                <Input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="bg-slate-800 border-slate-600 text-slate-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Role</label>
                <Input
                  type="text"
                  value={user?.role || ''}
                  disabled
                  className="bg-slate-800 border-slate-600 text-slate-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Organization ID</label>
                <Input
                  type="text"
                  value={user?.org_id || ''}
                  disabled
                  className="bg-slate-800 border-slate-600 text-slate-400 font-mono text-xs"
                />
              </div>
              <Button className="bg-red-600 hover:bg-red-700 text-white">
                Update Profile
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="max-w-2xl">
          <div className="bg-slate-900 rounded-lg p-6 border border-slate-700">
            <h2 className="text-xl font-bold text-white mb-6">Notification Preferences</h2>
            <div className="space-y-4">
              <label className="flex items-center p-4 bg-slate-800 rounded-lg cursor-pointer hover:bg-slate-700 transition-colors">
                <input
                  type="checkbox"
                  checked={notifications.emailOnNewIncident}
                  onChange={(e) =>
                    setNotifications({
                      ...notifications,
                      emailOnNewIncident: e.target.checked,
                    })
                  }
                  className="w-4 h-4 accent-red-600"
                />
                <div className="ml-4 flex-1">
                  <p className="text-white font-medium">Email on New Incident</p>
                  <p className="text-slate-400 text-sm">Receive alerts when new incidents are created</p>
                </div>
              </label>

              <label className="flex items-center p-4 bg-slate-800 rounded-lg cursor-pointer hover:bg-slate-700 transition-colors">
                <input
                  type="checkbox"
                  checked={notifications.emailOnCriticalVuln}
                  onChange={(e) =>
                    setNotifications({
                      ...notifications,
                      emailOnCriticalVuln: e.target.checked,
                    })
                  }
                  className="w-4 h-4 accent-red-600"
                />
                <div className="ml-4 flex-1">
                  <p className="text-white font-medium">Critical Vulnerability Alerts</p>
                  <p className="text-slate-400 text-sm">Get notified about critical and high vulnerabilities</p>
                </div>
              </label>

              <label className="flex items-center p-4 bg-slate-800 rounded-lg cursor-pointer hover:bg-slate-700 transition-colors">
                <input
                  type="checkbox"
                  checked={notifications.emailOnIncidentUpdate}
                  onChange={(e) =>
                    setNotifications({
                      ...notifications,
                      emailOnIncidentUpdate: e.target.checked,
                    })
                  }
                  className="w-4 h-4 accent-red-600"
                />
                <div className="ml-4 flex-1">
                  <p className="text-white font-medium">Incident Updates</p>
                  <p className="text-slate-400 text-sm">Be notified when assigned incidents are updated</p>
                </div>
              </label>

              <label className="flex items-center p-4 bg-slate-800 rounded-lg cursor-pointer hover:bg-slate-700 transition-colors">
                <input
                  type="checkbox"
                  checked={notifications.emailDigest}
                  onChange={(e) =>
                    setNotifications({
                      ...notifications,
                      emailDigest: e.target.checked,
                    })
                  }
                  className="w-4 h-4 accent-red-600"
                />
                <div className="ml-4 flex-1">
                  <p className="text-white font-medium">Daily Digest</p>
                  <p className="text-slate-400 text-sm">Receive a daily summary of security activities</p>
                </div>
              </label>

              <Button className="bg-red-600 hover:bg-red-700 text-white mt-6">
                Save Preferences
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="max-w-2xl">
          <div className="bg-slate-900 rounded-lg p-6 border border-slate-700">
            <h2 className="text-xl font-bold text-white mb-6">Security Settings</h2>
            <div className="space-y-6">
              <div>
                <h3 className="font-bold text-white mb-3">Change Password</h3>
                <div className="space-y-4">
                  <Input
                    type="password"
                    placeholder="Current password"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                  <Input
                    type="password"
                    placeholder="New password"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                  <Input
                    type="password"
                    placeholder="Confirm new password"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                  <Button className="bg-red-600 hover:bg-red-700 text-white">
                    Update Password
                  </Button>
                </div>
              </div>

              <div className="pt-6 border-t border-slate-700">
                <h3 className="font-bold text-white mb-3">Two-Factor Authentication</h3>
                <p className="text-slate-400 text-sm mb-4">Add an extra layer of security to your account</p>
                <Button className="bg-slate-700 hover:bg-slate-600 text-white">
                  Enable 2FA
                </Button>
              </div>

              <div className="pt-6 border-t border-slate-700">
                <h3 className="font-bold text-white mb-3">Active Sessions</h3>
                <p className="text-slate-400 text-sm mb-4">Manage your active sessions across devices</p>
                <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800">
                  View Sessions
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Integrations Tab */}
      {activeTab === 'integrations' && (
        <div className="max-w-2xl">
          <div className="bg-slate-900 rounded-lg p-6 border border-slate-700">
            <h2 className="text-xl font-bold text-white mb-6">API & Integrations</h2>
            <div className="space-y-4">
              <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
                <h3 className="font-bold text-white mb-2">API Keys</h3>
                <p className="text-slate-400 text-sm mb-4">Create API keys for programmatic access</p>
                <Button className="bg-red-600 hover:bg-red-700 text-white">
                  Generate New Key
                </Button>
              </div>

              <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
                <h3 className="font-bold text-white mb-2">Webhooks</h3>
                <p className="text-slate-400 text-sm mb-4">Configure webhooks for real-time event notifications</p>
                <Button className="bg-slate-700 hover:bg-slate-600 text-white">
                  Manage Webhooks
                </Button>
              </div>

              <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
                <h3 className="font-bold text-white mb-2">Connected Services</h3>
                <p className="text-slate-400 text-sm mb-4">Connect with your favorite security tools</p>
                <div className="flex gap-2 flex-wrap">
                  <Button variant="outline" className="border-slate-600 text-slate-300">Slack</Button>
                  <Button variant="outline" className="border-slate-600 text-slate-300">Jira</Button>
                  <Button variant="outline" className="border-slate-600 text-slate-300">ServiceNow</Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
