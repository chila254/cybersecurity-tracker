'use client'

import { Button } from '@/components/ui/button'
import { Trash2, CheckCircle, Clock, Lock } from 'lucide-react'
import { useState } from 'react'

interface BulkActionBarProps {
  selectedCount: number
  onBulkStatusChange: (status: string) => Promise<void>
  onBulkDelete: () => Promise<void>
  onClose: () => void
}

export function BulkActionBar({
  selectedCount,
  onBulkStatusChange,
  onBulkDelete,
  onClose,
}: BulkActionBarProps) {
  const [loading, setLoading] = useState(false)

  if (selectedCount === 0) return null

  const handleStatusChange = async (status: string) => {
    setLoading(true)
    try {
      await onBulkStatusChange(status)
      onClose()
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm(`Delete ${selectedCount} incident(s)? This cannot be undone.`)) return
    setLoading(true)
    try {
      await onBulkDelete()
      onClose()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-slate-900 border-t border-slate-700 p-4 z-40">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-white font-medium">{selectedCount} incident(s) selected</span>
          <div className="w-px h-6 bg-slate-700" />
          
          <div className="flex gap-2">
            <button
              onClick={() => handleStatusChange('INVESTIGATING')}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-2 bg-yellow-900/30 text-yellow-300 rounded hover:bg-yellow-900/50 disabled:opacity-50"
            >
              <Clock className="h-4 w-4" />
              Investigating
            </button>
            
            <button
              onClick={() => handleStatusChange('RESOLVED')}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-2 bg-green-900/30 text-green-300 rounded hover:bg-green-900/50 disabled:opacity-50"
            >
              <CheckCircle className="h-4 w-4" />
              Resolved
            </button>
            
            <button
              onClick={() => handleStatusChange('CLOSED')}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-2 bg-slate-800 text-slate-300 rounded hover:bg-slate-700 disabled:opacity-50"
            >
              <Lock className="h-4 w-4" />
              Closed
            </button>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleDelete}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-red-900/30 text-red-300 rounded hover:bg-red-900/50 disabled:opacity-50"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </button>
          
          <Button
            onClick={onClose}
            variant="outline"
            className="bg-slate-800 border-slate-600 text-white hover:bg-slate-700"
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  )
}
