'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Trash2, Plus, Shield, Eye, Edit2 } from 'lucide-react'

interface TeamMember {
  id: string
  email: string
  name: string
  role: 'ADMIN' | 'ANALYST' | 'VIEWER'
  created_at: string
  last_login?: string
}

export default function TeamManagementPage() {
  const [members, setMembers] = useState<TeamMember[]>([])
  const [loading, setLoading] = useState(true)
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState<'ANALYST' | 'VIEWER'>('ANALYST')
  const [inviting, setInviting] = useState(false)

  useEffect(() => {
    fetchTeamMembers()
  }, [])

  const fetchTeamMembers = async () => {
    setLoading(true)
    try {
      const { data } = await apiClient.get('/auth/team')
      if (data) setMembers(data)
    } catch (error) {
      console.error('Failed to fetch team members:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault()
    setInviting(true)
    try {
      await apiClient.post('/auth/invite', {
        email: inviteEmail,
        role: inviteRole
      })
      setInviteEmail('')
      setShowInviteModal(false)
      fetchTeamMembers()
    } catch (error) {
      console.error('Failed to invite member:', error)
    } finally {
      setInviting(false)
    }
  }

  const handleRemove = async (memberId: string) => {
    if (!window.confirm('Remove this team member?')) return
    try {
      await apiClient.delete(`/auth/team/${memberId}`)
      fetchTeamMembers()
    } catch (error) {
      console.error('Failed to remove member:', error)
    }
  }

  const handleChangeRole = async (memberId: string, newRole: 'ADMIN' | 'ANALYST' | 'VIEWER') => {
    try {
      await apiClient.patch(`/auth/team/${memberId}`, { role: newRole })
      fetchTeamMembers()
    } catch (error) {
      console.error('Failed to change role:', error)
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return <Shield className="h-4 w-4 text-red-400" />
      case 'ANALYST':
        return <Edit2 className="h-4 w-4 text-blue-400" />
      case 'VIEWER':
        return <Eye className="h-4 w-4 text-slate-400" />
      default:
        return null
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return 'bg-red-900/20 text-red-300'
      case 'ANALYST':
        return 'bg-blue-900/20 text-blue-300'
      case 'VIEWER':
        return 'bg-slate-700/20 text-slate-300'
      default:
        return 'bg-slate-700/20 text-slate-300'
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 dark:bg-black p-4 md:p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Team Management</h1>
            <p className="text-slate-400">Manage team members and their permissions</p>
          </div>
          <Button
            onClick={() => setShowInviteModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Invite Member
          </Button>
        </div>

        {/* Invite Modal */}
        {showInviteModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-slate-900 rounded-lg max-w-md w-full border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Invite Team Member</h2>
              <form onSubmit={handleInvite} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
                  <Input
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="member@example.com"
                    className="bg-slate-800 border-slate-600 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Role</label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value as 'ANALYST' | 'VIEWER')}
                    className="w-full bg-slate-800 border border-slate-600 rounded text-white p-2"
                  >
                    <option value="ANALYST">Analyst (Create/Update)</option>
                    <option value="VIEWER">Viewer (Read-only)</option>
                  </select>
                </div>
                <div className="flex gap-2 justify-end">
                  <Button
                    type="button"
                    onClick={() => setShowInviteModal(false)}
                    variant="outline"
                    className="bg-slate-800 border-slate-600 text-white"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={inviting}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {inviting ? 'Inviting...' : 'Send Invite'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Team Members List */}
        <div className="bg-slate-900 rounded-lg border border-slate-700 overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-slate-400">Loading team members...</div>
          ) : members.length === 0 ? (
            <div className="p-8 text-center text-slate-400">No team members yet</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-800 border-b border-slate-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Email</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Role</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Joined</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">Last Active</th>
                    <th className="px-6 py-3 text-right text-sm font-semibold text-slate-300">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {members.map(member => (
                    <tr key={member.id} className="hover:bg-slate-800/50 transition-colors">
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-medium text-white">{member.name || 'Unknown'}</div>
                          <div className="text-sm text-slate-400">{member.email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <select
                            value={member.role}
                            onChange={(e) => handleChangeRole(member.id, e.target.value as any)}
                            className={`px-3 py-1 rounded text-sm font-medium border-0 ${getRoleColor(member.role)}`}
                          >
                            <option value="ADMIN">Admin</option>
                            <option value="ANALYST">Analyst</option>
                            <option value="VIEWER">Viewer</option>
                          </select>
                          {getRoleIcon(member.role)}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-400">
                        {new Date(member.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-400">
                        {member.last_login ? new Date(member.last_login).toLocaleDateString() : 'Never'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleRemove(member.id)}
                          className="p-2 text-red-400 hover:bg-red-900/20 rounded transition-colors"
                          title="Remove member"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Role Information */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
            <div className="flex items-start gap-3">
              <Shield className="h-5 w-5 text-red-400 mt-1" />
              <div>
                <h3 className="font-semibold text-white">Admin</h3>
                <p className="text-sm text-slate-400 mt-1">Full access to all features and settings</p>
              </div>
            </div>
          </div>
          <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
            <div className="flex items-start gap-3">
              <Edit2 className="h-5 w-5 text-blue-400 mt-1" />
              <div>
                <h3 className="font-semibold text-white">Analyst</h3>
                <p className="text-sm text-slate-400 mt-1">Create and update incidents and vulnerabilities</p>
              </div>
            </div>
          </div>
          <div className="bg-slate-900 rounded-lg border border-slate-700 p-6">
            <div className="flex items-start gap-3">
              <Eye className="h-5 w-5 text-slate-400 mt-1" />
              <div>
                <h3 className="font-semibold text-white">Viewer</h3>
                <p className="text-sm text-slate-400 mt-1">Read-only access to incidents and reports</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
